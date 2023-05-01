# Generated by Django 4.1.1 on 2023-04-30 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aviato', '0011_alter_applications_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='first_name',
            field=models.CharField(blank=True, default='Неизвестно', max_length=100, null=True, verbose_name='Имя'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='role',
            field=models.CharField(choices=[('Роль не выдана', 'Роль не выдана'), ('Упаковщик-Логист', 'Упаковщик-Логист'), ('Снабженец', 'Снабженец'), ('Админ', 'Админ'), ('Менеджер', 'Менеджер'), ('Логист', 'Логист'), ('Оператор', 'Оператор'), ('Водитель', 'Водитель'), ('Упаковщик', 'Упаковщик')], default='Роль не выдана', max_length=200, verbose_name='Роль пользователя'),
        ),
    ]
