# Generated by Django 4.0.5 on 2022-07-30 11:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aviato', '0007_applications_phone'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='first_name',
            field=models.CharField(default=1, max_length=100, verbose_name='Имя'),
            preserve_default=False,
        ),
    ]