# Generated by Django 5.1.5 on 2025-02-14 03:20

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehicle', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SpecialVehicleOrderCalendar',
            fields=[
            ],
            options={
                'verbose_name': 'Календарь занятости спецтранспорта',
                'verbose_name_plural': 'Календарь занятости спецтранспорта',
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('vehicle.specialvehicle',),
        ),
        migrations.AlterField(
            model_name='specialvehicleorderchange',
            name='special_vehicle_order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='change_special_vehicle_order', to='vehicle.specialvehicleorder', verbose_name='Заказ СпецТехники'),
        ),
        migrations.CreateModel(
            name='RegulationsMaintenance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('spare_part_name', models.CharField(max_length=255, verbose_name='Наименование запчасти')),
                ('replacement_date', models.DateField(verbose_name='Дата замены')),
                ('mileage_on_equipment', models.CharField(max_length=128, verbose_name='Пробег на технике')),
                ('spare_part_hours', models.CharField(max_length=128, verbose_name='Моточасы на новую запчасть')),
                ('cost_of_spare_part', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Стоимость запчасти')),
                ('created_by', models.ForeignKey(blank=True, db_column='created_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Создано пользователем')),
                ('updated_by', models.ForeignKey(blank=True, db_column='updated_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Изменено пользователем')),
                ('vehicle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vehicle.specialvehicle', verbose_name='Спецтехника')),
            ],
            options={
                'verbose_name': 'Регламент обслуживания спецтехники',
                'verbose_name_plural': 'Регламенты обслуживания спецтехники',
                'db_table': 'regulations_maintenance',
            },
        ),
    ]
