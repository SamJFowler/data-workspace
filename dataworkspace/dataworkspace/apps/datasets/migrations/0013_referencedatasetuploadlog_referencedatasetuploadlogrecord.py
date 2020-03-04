# Generated by Django 2.2.3 on 2019-09-02 09:30

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('datasets', '0012_auto_20190827_1553'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReferenceDatasetUploadLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID',),),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                (
                    'created_by',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='created+',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    'reference_dataset',
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='datasets.ReferenceDataset',),
                ),
                (
                    'updated_by',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name='updated+',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={'ordering': ('created_date',)},
        ),
        migrations.CreateModel(
            name='ReferenceDatasetUploadLogRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID',),),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                (
                    'status',
                    models.IntegerField(
                        choices=[
                            (1, 'Record added successfully'),
                            (2, 'Record updated successfully'),
                            (3, 'Record upload failed'),
                        ]
                    ),
                ),
                ('row_data', django.contrib.postgres.fields.jsonb.JSONField()),
                ('errors', django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                (
                    'upload_log',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='records',
                        to='datasets.ReferenceDatasetUploadLog',
                    ),
                ),
            ],
            options={'ordering': ('created_date',)},
        ),
    ]
