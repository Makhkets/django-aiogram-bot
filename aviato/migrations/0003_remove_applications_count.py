# Generated by Django 4.0.5 on 2022-07-29 11:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aviato', '0002_alter_applications_driver'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='applications',
            name='count',
        ),
    ]
