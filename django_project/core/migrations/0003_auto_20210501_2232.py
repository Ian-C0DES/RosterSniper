# Generated by Django 3.2 on 2021-05-01 22:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_suggestedschool_2'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subject',
            options={'ordering': ['short_title']},
        ),
        migrations.AlterModelOptions(
            name='term',
            options={'ordering': ['-code_std']},
    ),
        migrations.AlterModelOptions(
            name='favorite',
            options={'ordering': ['section__school', 'section']},
        ),
    ]
