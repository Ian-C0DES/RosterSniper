# Generated by Django 4.1 on 2022-11-01 20:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20210501_2232'),
    ]

    operations = [
        migrations.AddField(
            model_name='favorite',
            name='phone_notify',
            field=models.BooleanField(default=False),
        ),
    ]
