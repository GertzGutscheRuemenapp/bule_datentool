# Generated by Django 3.2.5 on 2021-09-04 12:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datentool_backend', '0006_years_bm_create_uuid'),
    ]

    operations = [
        migrations.RenameField(
            model_name='placefield',
            old_name='attribure',
            new_name='attribute',
        ),
    ]