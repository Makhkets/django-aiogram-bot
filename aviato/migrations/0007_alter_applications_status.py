# Generated by Django 4.1.1 on 2023-04-14 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aviato', '0006_alter_applications_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applications',
            name='status',
            field=models.CharField(blank=True, default='Ожидание подтверждения', max_length=200, null=True, verbose_name='Статус'),
        ),
    ]
