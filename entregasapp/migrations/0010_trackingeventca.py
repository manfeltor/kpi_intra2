# Generated by Django 5.0.4 on 2024-05-14 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entregasapp', '0009_rename_srvisits_srvisit'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrackingEventCA',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tracking_number', models.CharField(max_length=100)),
                ('data', models.JSONField()),
            ],
        ),
    ]