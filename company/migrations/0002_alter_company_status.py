# Generated by Django 5.0.12 on 2025-02-25 09:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('company', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='status',
            field=models.CharField(choices=[('active', 'Активный'), ('inactive', 'Не активный')], default='active', max_length=16, verbose_name='Статус'),
        ),
    ]
