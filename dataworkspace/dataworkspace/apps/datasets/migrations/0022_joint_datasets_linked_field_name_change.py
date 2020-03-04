# Generated by Django 2.2.4 on 2019-11-15 12:29

from django.db import migrations


def update_joint_dataset_version_number(apps, schema_editor):
    ReferenceDataset = apps.get_model('datasets', 'ReferenceDataset')
    joint_datasets = ReferenceDataset.objects.filter(is_joint_dataset=True, deleted=False)
    for dataset in joint_datasets:
        dataset.major_version += 1
        dataset.minor_version = 0
        dataset.save()


class Migration(migrations.Migration):

    dependencies = [('datasets', '0021_dataset_access_criteria')]

    operations = [migrations.RunPython(update_joint_dataset_version_number, migrations.RunPython.noop)]
