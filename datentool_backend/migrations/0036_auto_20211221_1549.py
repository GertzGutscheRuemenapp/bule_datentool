# Generated by Django 3.2.8 on 2021-12-21 14:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('datentool_backend', '0035_auto_20211220_1446'),
    ]

    operations = [
        migrations.CreateModel(
            name='ScenarioCapacity',
            fields=[
                ('capacity_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='datentool_backend.capacity')),
                ('scenario', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='datentool_backend.scenario')),
                ('status_quo', models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='scenario_capacities', to='datentool_backend.capacity')),
            ],
            bases=('datentool_backend.capacity',),
        ),
        migrations.CreateModel(
            name='ScenarioDemandRate',
            fields=[
                ('demandrate_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='datentool_backend.demandrate')),
                ('scenario', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='datentool_backend.scenario')),
            ],
            bases=('datentool_backend.demandrate',),
        ),
        migrations.CreateModel(
            name='ScenarioPlace',
            fields=[
                ('place_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='datentool_backend.place')),
                ('scenario', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='datentool_backend.scenario')),
                ('status_quo', models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='scenario_places', to='datentool_backend.place')),
            ],
            bases=('datentool_backend.place',),
        ),
        migrations.RemoveField(
            model_name='service',
            name='quota',
        ),
        migrations.AddField(
            model_name='service',
            name='quota_type',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='Quota',
        ),
    ]