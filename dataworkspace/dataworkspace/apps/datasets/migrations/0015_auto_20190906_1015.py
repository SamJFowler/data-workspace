# Generated by Django 2.2.3 on 2019-09-06 10:15

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [('core', '0001_initial'), ('datasets', '0014_auto_20190906_0934')]

    operations = [
        migrations.AddField(
            model_name='sourcetable',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2019, 9, 6, 10, 15, 24, 868019),),
            preserve_default=False,
        ),
        migrations.AddField(model_name='sourcetable', name='modified_date', field=models.DateTimeField(auto_now=True),),
        migrations.CreateModel(
            name='CustomDatasetQuery',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID',),),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('query', models.TextField()),
                (
                    'frequency',
                    models.IntegerField(
                        choices=[(1, 'Daily'), (2, 'Weekly'), (3, 'Monthly'), (4, 'Quarterly'), (5, 'Annually'),]
                    ),
                ),
                ('database', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Database'),),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='datasets.DataSet',),),
            ],
            options={'verbose_name': 'SQL Query', 'verbose_name_plural': 'SQL Queries'},
        ),
    ]
