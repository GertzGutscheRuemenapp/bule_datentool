# Generated by Django 3.2.8 on 2022-01-18 15:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datentool_backend', '0050_auto_20220118_1201'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='capacity',
            unique_together={('place', 'service', 'from_year', 'scenario')},
        ),
    ]
