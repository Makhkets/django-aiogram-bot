# Generated by Django 4.0.5 on 2022-07-30 08:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aviato', '0005_alter_applications_options_alter_profile_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='rolecode',
            options={'verbose_name': 'Коды', 'verbose_name_plural': 'Коды'},
        ),
        migrations.RemoveField(
            model_name='applications',
            name='additional_information',
        ),
        migrations.RemoveField(
            model_name='applications',
            name='full_name',
        ),
    ]