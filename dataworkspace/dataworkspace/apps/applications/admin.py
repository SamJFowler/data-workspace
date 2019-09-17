from datetime import datetime
from itertools import product

from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.models import (
    User,
    Permission,
)
from django.db.models import Count, Max, Min, Sum, F, Func, Value, Q
from django.db.models.functions import Least

from dataworkspace.apps.applications.models import (
    ApplicationInstance,
    ApplicationInstanceReport,
    ApplicationTemplate,
)
from dataworkspace.apps.applications.utils import application_instance_max_cpu


@admin.register(ApplicationInstance)
class ApplicationInstanceAdmin(admin.ModelAdmin):

    list_display = ('owner', 'public_host', 'created_date', )
    fieldsets = [
        (None, {
            'fields': [
                'owner',
                'public_host',
                'created_date',
                'state',
                'spawner_application_instance_id',
                'max_cpu',
            ]
        }),
    ]
    readonly_fields = (
        'owner', 'public_host', 'created_date', 'spawner_application_instance_id', 'state',
        'max_cpu',
    )

    def has_add_permission(self, request):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(state__in=['SPAWNING', 'RUNNING'])

    def max_cpu(self, obj):
        try:
            max_cpu, ts_at_max = application_instance_max_cpu(obj)
        except ValueError as exception:
            return exception.args[0] if exception.args else 'Error'

        return '{0:.2f}% at {1}'.format(
            max_cpu,
            datetime.datetime.fromtimestamp(ts_at_max).strftime('%-I:%M %p').replace('AM', 'a.m.').replace('PM', 'p.m'),
        )

    max_cpu.short_description = 'Max recent CPU'

    def get_form(self, request, obj=None, change=False, **kwargs):
        kwargs.update({
            'help_texts': {
                'max_cpu': ('The highest CPU usage in the past two hours.'
                            'The application will be stopped automatically '
                            'if the usage is less than 1% for two hours.'),
            },
        })
        return super().get_form(request, obj, change, **kwargs)


class ApplicationFilter(SimpleListFilter):
    title = 'Filter by application'
    parameter_name = 'application_template__name'
    template = 'admin/application_instance_report_filter.html'

    def lookups(self, request, model_admin):
        return tuple(
            (app.name, app.nice_name)
            for app in ApplicationTemplate.objects.all().order_by('nice_name')
        )

    def queryset(self, request, queryset):
        try:
            queryset_filter = {
                'application_template__name': request.GET['application_template__name'],
            }
        except KeyError:
            queryset_filter = {}
        return queryset.filter(**queryset_filter)


class ApplicationGroup(SimpleListFilter):
    # Slight mis-use of a filter to allow a dynamic group by in the
    # surrounding report
    title = 'Group by'
    parameter_name = 'group_by'
    template = 'admin/application_instance_report_filter.html'

    def lookups(self, request, model_admin):
        return (
            ('user_and_application', 'User and application'),
            ('user', 'User'),
            ('application', 'Application'),
        )

    def choices(self, changelist):
        for i, (lookup, title) in enumerate(self.lookup_choices):
            yield {
                'selected': self.value() == str(lookup) or (i == 0 and self.value() is None),
                'query_string': changelist.get_query_string({self.parameter_name: lookup}),
                'display': title,
            }

    def queryset(self, request, queryset):
        # No extra filtering, but this is tightly coupled to behaviour in
        # ApplicationInstanceReportAdmin that groups
        return queryset


@admin.register(ApplicationInstanceReport)
class ApplicationInstanceReportAdmin(admin.ModelAdmin):
    change_list_template = 'admin/application_instance_report_change_list.html'
    date_hierarchy = 'created_date'

    list_filter = (
        (ApplicationFilter, ApplicationGroup,)
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        # We want to display times to second precision, so we truncate the
        # timestamps to second precision _before_ summing, to avoid issues
        # where the totals of the rows each don't add up to the bottom total
        metrics = {
            'num_launched': Count('id'),
            # NULL values are ordered as greater than non-NULL values, so to order rows without
            # runtime as lower in the list as those that have runtime, but still order rows with
            # runtime in decreasing order, we need an extra field
            'has_runtime': Least(Count(F('spawner_stopped_at') - F('spawner_created_at')), 1),
            'num_with_runtime': Count(F('spawner_stopped_at') - F('spawner_created_at')),
            'min_runtime': Min(
                Func(Value('second'), F('spawner_stopped_at'), function='date_trunc') -
                Func(Value('second'), F('spawner_created_at'), function='date_trunc')
            ),
            'max_runtime': Max(
                Func(Value('second'), F('spawner_stopped_at'), function='date_trunc') -
                Func(Value('second'), F('spawner_created_at'), function='date_trunc')
            ),
            'total_runtime': Sum(
                Func(Value('second'), F('spawner_stopped_at'), function='date_trunc') -
                Func(Value('second'), F('spawner_created_at'), function='date_trunc')
            ),
        }

        group_by_fields = {
            'user_and_application': ['owner__username', 'application_template__nice_name'],
            'user': ['owner__username'],
            'application': ['application_template__nice_name'],
        }[request.GET.get('group_by', 'user_and_application')]

        summary_with_applications = list(
            qs
            .values(*group_by_fields)
            .annotate(**metrics)
            .order_by(*(
                ['-has_runtime', '-total_runtime', '-num_launched', '-max_runtime'] + group_by_fields
            ))
        )

        perm = list(Permission.objects.filter(codename='start_all_applications'))
        users = User.objects.filter(
            Q(groups__permissions__in=perm) | Q(user_permissions__in=perm) | Q(is_superuser=True)
        ).distinct().order_by('username')

        try:
            app_filter = {
                'name__in': [request.GET['application_template__name']]
            }
        except KeyError:
            app_filter = {}

        def group_by_user_missing_rows():
            users_with_applications = set(
                item['owner__username']
                for item in summary_with_applications
            )
            return [
                {
                    'owner__username': user.username,
                    'application_template__nice_name': None,
                    'num_launched': 0,
                    'has_runtime': 0,
                    'num_with_runtime': 0,
                }
                for user in users
                if user.username not in users_with_applications
            ]

        def group_by_application_missing_rows():
            application_templates = list(ApplicationTemplate.objects.filter(**app_filter).order_by('nice_name'))
            applications_run = set(
                item['application_template__nice_name']
                for item in summary_with_applications
            )
            return [
                {
                    'owner__username': None,
                    'application_template__nice_name': application_template.nice_name,
                    'num_launched': 0,
                    'has_runtime': 0,
                    'num_with_runtime': 0,
                }
                for application_template in application_templates
                if application_template.nice_name not in applications_run
            ]

        def group_by_user_and_application_missing_rows():
            application_templates = list(ApplicationTemplate.objects.filter(**app_filter).order_by('nice_name'))
            users_with_applications = set(
                (item['owner__username'], item['application_template__nice_name'])
                for item in summary_with_applications
            )
            return [
                {
                    'owner__username': user.username,
                    'application_template__nice_name': application_template.nice_name,
                    'num_launched': 0,
                    'has_runtime': 0,
                    'num_with_runtime': 0,
                }
                for user, application_template in product(users, application_templates)
                if (user.username, application_template.nice_name) not in users_with_applications
            ]

        summary_without_applications = (
            group_by_user_missing_rows() if request.GET.get('group_by') == 'user' else
            group_by_application_missing_rows() if request.GET.get('group_by') == 'application' else
            group_by_user_and_application_missing_rows()
        )

        response.context_data['summary'] = summary_with_applications + summary_without_applications

        response.context_data['summary_total'] = dict(
            qs.aggregate(**metrics)
        )

        return response
