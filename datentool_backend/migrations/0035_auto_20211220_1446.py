# Generated by Django 3.2.8 on 2021-12-20 13:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datentool_backend', '0034_remove_popstatentry_age'),
    ]

    operations = [
        migrations.AddField(
            model_name='demandrate',
            name='value',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='demandrateset',
            name='service',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.RESTRICT, to='datentool_backend.service'),
            preserve_default=False,
        ),
    ]