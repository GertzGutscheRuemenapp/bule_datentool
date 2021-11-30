# Generated by Django 3.2.6 on 2021-11-30 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datentool_backend', '0021_auto_20211129_1353'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='can_create_scenarios',
            new_name='can_create_project',
        ),
        migrations.AlterField(
            model_name='project',
            name='users',
            field=models.ManyToManyField(blank=True, related_name='shared_with_users', to='datentool_backend.Profile'),
        ),
    ]
