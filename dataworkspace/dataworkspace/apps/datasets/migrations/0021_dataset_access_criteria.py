# Generated by Django 2.2.4 on 2019-10-22 15:14

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0020_auto_20191019_1923'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='eligibility_criteria',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=256), null=True, size=None),
        ),
    ]
