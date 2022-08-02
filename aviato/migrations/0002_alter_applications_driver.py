# Generated by Django 4.0.5 on 2022-07-29 10:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('aviato', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applications',
            name='driver',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='drive_user', to='aviato.profile', verbose_name='Водитель который принял заказ'),
        ),
    ]