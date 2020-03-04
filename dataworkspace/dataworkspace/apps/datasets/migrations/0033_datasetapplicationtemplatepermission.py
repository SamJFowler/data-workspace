# Generated by Django 2.2.8 on 2019-12-27 11:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('applications', '0016_auto_20191216_1202'),
        ('datasets', '0032_auto_20191227_1109'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataSetApplicationTemplatePermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID',),),
                (
                    'application_template',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to='applications.ApplicationTemplate',
                    ),
                ),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='datasets.DataSet',),),
            ],
            options={
                'db_table': 'app_datasetapplicationtemplatepermission',
                'unique_together': {('dataset', 'application_template')},
            },
        )
    ]
