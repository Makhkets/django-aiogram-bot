# Generated by Django 4.0.5 on 2022-08-13 05:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aviato', '0019_alter_applications_create_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='Products',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.CharField(max_length=1000, verbose_name='Товар')),
                ('count', models.IntegerField(verbose_name='Количество')),
                ('opt_price', models.PositiveIntegerField(verbose_name='Оптовая Цена')),
                ('availability', models.BooleanField(default=True, verbose_name='Наличие')),
                ('photo', models.CharField(blank=True, max_length=3000, null=True, verbose_name='Фото')),
                ('product_suum', models.PositiveIntegerField(blank=True, null=True, verbose_name='Сумма товара')),
                ('product_percent', models.FloatField(blank=True, null=True, verbose_name='2.5% От Суммы Товара')),
                ('fake_count', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Товары',
                'verbose_name_plural': 'Товары',
            },
        ),
        migrations.RemoveField(
            model_name='applications',
            name='photo',
        ),
        migrations.AddField(
            model_name='applications',
            name='bool_count',
            field=models.BooleanField(default=True, verbose_name='Хватает ли количество'),
        ),
        migrations.AddField(
            model_name='applications',
            name='bool_status',
            field=models.BooleanField(blank=True, null=True, verbose_name='Подтвержден'),
        ),
        migrations.AddField(
            model_name='applications',
            name='checks_document',
            field=models.CharField(blank=True, max_length=1000, null=True, verbose_name='Чек'),
        ),
        migrations.AddField(
            model_name='applications',
            name='products',
            field=models.ManyToManyField(to='aviato.products', verbose_name='Привязанный товар'),
        ),
    ]
