# Generated by Django 5.1.5 on 2025-01-30 05:50

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('employee', '0001_initial'),
        ('project', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SpecialVehicle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('number', models.CharField(blank=True, default='', max_length=255, verbose_name='Номер')),
                ('brand', models.CharField(blank=True, default='', max_length=255, verbose_name='Марка')),
                ('model', models.CharField(blank=True, default='', max_length=255, verbose_name='Модель')),
                ('year', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Год')),
                ('description', models.CharField(blank=True, default='', max_length=255, verbose_name='Описание')),
                ('status', models.CharField(blank=True, choices=[(None, 'Неизвестный'), ('active', 'Активный'), ('deleted', 'Удалён')], default='active', max_length=255, null=True, verbose_name='Статус')),
                ('created_by', models.ForeignKey(blank=True, db_column='created_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Создано пользователем')),
                ('default_driver_employee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='default_driver_employee', to='employee.employee', verbose_name='Основной водитель')),
                ('owner_employee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='owner_employee', to='employee.employee', verbose_name='Собственник')),
                ('partner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='project.partner', verbose_name='Партнёр')),
                ('updated_by', models.ForeignKey(blank=True, db_column='updated_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Изменено пользователем')),
            ],
            options={
                'verbose_name': 'Спецтехника',
                'verbose_name_plural': 'Спецтехника',
                'db_table': 'special_vehicle',
            },
        ),
        migrations.CreateModel(
            name='SpecialVehicleOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('starting_at', models.DateTimeField(blank=True, null=True, verbose_name='Начало планируемое')),
                ('started_at', models.DateTimeField(blank=True, null=True, verbose_name='Начало фактическое')),
                ('ending_at', models.DateTimeField(blank=True, null=True, verbose_name='Завершение планируемое')),
                ('ended_at', models.DateTimeField(blank=True, null=True, verbose_name='Завершение фактическое')),
                ('status', models.CharField(blank=True, choices=[('created', 'Создано'), ('confirmed', 'Подтверждено'), ('done', 'Выполнено'), ('canceled', 'Отменено')], default='created', max_length=255, null=True, verbose_name='Статус')),
                ('notes', models.CharField(blank=True, default='', max_length=255, verbose_name='Примечания')),
                ('created_by', models.ForeignKey(blank=True, db_column='created_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Создано пользователем')),
                ('project', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='project.project', verbose_name='Проект')),
                ('special_vehicle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vehicle.specialvehicle', verbose_name='Спецтехника')),
                ('updated_by', models.ForeignKey(blank=True, db_column='updated_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Изменено пользователем')),
                ('work', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='project.work', verbose_name='Работа')),
            ],
            options={
                'verbose_name': 'Заказ СпецТехники',
                'verbose_name_plural': 'Заказы СпецТехники',
                'db_table': 'special_vehicle_order',
            },
        ),
        migrations.CreateModel(
            name='SpecialVehicleOrderChange',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('field', models.CharField(max_length=255, verbose_name='Поле')),
                ('old_value', models.CharField(blank=True, max_length=255, null=True, verbose_name='Старое значение')),
                ('new_value', models.CharField(blank=True, max_length=255, null=True, verbose_name='Новое значение')),
                ('created_by', models.ForeignKey(blank=True, db_column='created_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Создано пользователем')),
                ('special_vehicle_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vehicle.specialvehicleorder', verbose_name='Заказ СпецТехники')),
                ('updated_by', models.ForeignKey(blank=True, db_column='updated_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Изменено пользователем')),
            ],
            options={
                'verbose_name': 'История заявки',
                'verbose_name_plural': 'Истории заявки',
                'db_table': 'special_vehicle_order_change',
            },
        ),
        migrations.CreateModel(
            name='SpecialVehicleOrderComment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('body', models.TextField(verbose_name='Текст сообщения')),
                ('created_by', models.ForeignKey(blank=True, db_column='created_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Создано пользователем')),
                ('employee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='employee.employee', verbose_name='Сотрудник')),
                ('special_vehicle_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vehicle.specialvehicleorder', verbose_name='Заказ СпецТехники')),
                ('updated_by', models.ForeignKey(blank=True, db_column='updated_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Изменено пользователем')),
            ],
            options={
                'verbose_name': 'Комментарий по заявке',
                'verbose_name_plural': 'Комментарии по заявке',
                'db_table': 'special_vehicle_order_comment',
            },
        ),
        migrations.CreateModel(
            name='SpecialVehicleOrderEmployee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('type', models.CharField(choices=[('creator', 'Заказчик'), ('executor', 'Исполнитель'), ('driver', 'Водитель')], default='creator', max_length=255, verbose_name='')),
                ('created_by', models.ForeignKey(blank=True, db_column='created_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Создано пользователем')),
                ('employee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='employee.employee', verbose_name='Сотрудник')),
                ('special_vehicle_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vehicle.specialvehicleorder', verbose_name='Заказ СпецТехники')),
                ('updated_by', models.ForeignKey(blank=True, db_column='updated_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Изменено пользователем')),
            ],
            options={
                'verbose_name': '',
                'verbose_name_plural': '',
                'db_table': 'special_vehicle_order_employee',
            },
        ),
        migrations.CreateModel(
            name='SpecialVehicleType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('title', models.CharField(max_length=255, verbose_name='Название')),
                ('description', models.TextField(blank=True, default='', verbose_name='Описание')),
                ('created_by', models.ForeignKey(blank=True, db_column='created_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Создано пользователем')),
                ('parent_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='vehicle.specialvehicletype')),
                ('updated_by', models.ForeignKey(blank=True, db_column='updated_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Изменено пользователем')),
            ],
            options={
                'verbose_name': 'Тип спецтехники',
                'verbose_name_plural': 'Типы спецтехники',
                'db_table': 'special_vehicle_type',
            },
        ),
        migrations.AddField(
            model_name='specialvehicleorder',
            name='special_vehicle_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vehicle.specialvehicletype', verbose_name='Тип спецтехники'),
        ),
        migrations.CreateModel(
            name='SpecialVehicleDriver',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата изменения')),
                ('notes', models.CharField(blank=True, default='', max_length=255, verbose_name='Примечания')),
                ('created_by', models.ForeignKey(blank=True, db_column='created_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Создано пользователем')),
                ('employee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='employee.employee', verbose_name='Работник')),
                ('updated_by', models.ForeignKey(blank=True, db_column='updated_by', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='+', to=settings.AUTH_USER_MODEL, verbose_name='Изменено пользователем')),
                ('special_vehicle_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vehicle.specialvehicletype', verbose_name='Тип спецтехники')),
            ],
            options={
                'verbose_name': 'Водитель',
                'verbose_name_plural': 'Водители',
                'db_table': 'special_vehicle_driver',
            },
        ),
        migrations.AddField(
            model_name='specialvehicle',
            name='special_vehicle_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vehicle.specialvehicletype', verbose_name='Тип спецтехники'),
        ),
    ]
