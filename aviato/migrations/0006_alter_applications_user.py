# Generated by Django 4.2 on 2023-04-12 12:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('aviato', '0005_alter_profile_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applications',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='aviato.profile', verbose_name='Добавил'),
        ),
    ]
