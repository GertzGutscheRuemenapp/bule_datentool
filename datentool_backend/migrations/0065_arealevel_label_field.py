# Generated by Django 3.2.11 on 2022-01-26 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datentool_backend', '0064_rename_indicatortypefields_indicatortypefield'),
    ]

    operations = [
        migrations.AddField(
            model_name='arealevel',
            name='label_field',
            field=models.TextField(null=True),
        ),
    ]