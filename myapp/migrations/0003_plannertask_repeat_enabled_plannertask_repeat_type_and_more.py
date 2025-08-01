# Generated by Django 5.1.6 on 2025-03-22 06:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_plannertask'),
    ]

    operations = [
        migrations.AddField(
            model_name='plannertask',
            name='repeat_enabled',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='plannertask',
            name='repeat_type',
            field=models.CharField(blank=True, choices=[('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')], max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='plannertask',
            name='repeat_until',
            field=models.DateField(blank=True, null=True),
        ),
    ]
