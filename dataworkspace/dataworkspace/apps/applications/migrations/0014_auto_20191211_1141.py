# Generated by Django 2.2.8 on 2019-12-11 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [('applications', '0013_auto_20191210_1616')]

    operations = [
        migrations.AddIndex(
            model_name='applicationtemplate',
            index=models.Index(fields=['application_type'], name='app_applica_applica_dd47f1_idx'),
        )
    ]
