# Generated by Django 3.2.6 on 2021-12-09 09:42

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datentool_backend', '0031_alter_planningprocess_map_section'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='planningprocess',
            name='map_section',
        ),
        migrations.AlterField(
            model_name='projectsetting',
            name='project_area',
            field=django.contrib.gis.db.models.fields.MultiPolygonField(null=True, srid=4326),
        ),
    ]
