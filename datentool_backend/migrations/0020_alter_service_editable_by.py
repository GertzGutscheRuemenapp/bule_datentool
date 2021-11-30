# Generated by Django 3.2.8 on 2021-11-22 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datentool_backend', '0019_auto_20211116_1405'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='editable_by',
            field=models.ManyToManyField(blank=True, related_name='service_editable_by', to='datentool_backend.Profile'),
        ),
    ]
