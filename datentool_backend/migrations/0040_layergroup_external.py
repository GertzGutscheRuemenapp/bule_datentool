# Generated by Django 3.2.4 on 2022-01-06 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datentool_backend', '0039_alter_mapsymbol_symbol'),
    ]

    operations = [
        migrations.AddField(
            model_name='layergroup',
            name='external',
            field=models.BooleanField(default=False),
        ),
    ]
