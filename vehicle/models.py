from datetime import datetime

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.safestring import mark_safe

from core.models import DateUserMixin
from employee.models import Employee
from project.models import Partner, Project, Work

VEHICLE_STATUS_NULL = None
VEHICLE_STATUS_ACTIVE = 'active'
VEHICLE_STATUS_DELETED = 'deleted'

VEHICLE_STATUSES = (
    (VEHICLE_STATUS_NULL, 'Неизвестный'),
    (VEHICLE_STATUS_ACTIVE, 'Активный'),
    (VEHICLE_STATUS_DELETED, 'Удалён')
)

VEHICLE_ORDER_STATUS_CREATED = 'created'
VEHICLE_ORDER_STATUS_CONFIRMED = 'confirmed'
VEHICLE_ORDER_STATUS_CANCELED = 'canceled'
VEHICLE_ORDER_STATUS_DONE = 'done'

VEHICLE_ORDER_STATUSES = (
    (VEHICLE_ORDER_STATUS_CREATED, 'Создано'),
    (VEHICLE_ORDER_STATUS_CONFIRMED, 'Подтверждено'),
    (VEHICLE_ORDER_STATUS_DONE, 'Выполнено'),
    (VEHICLE_ORDER_STATUS_CANCELED, 'Отменено'),
)

VEHICLE_ORDER_EMPLOYEE_TYPE_CREATOR = 'creator'
VEHICLE_ORDER_EMPLOYEE_TYPE_EXECUTOR = 'executor'
VEHICLE_ORDER_EMPLOYEE_TYPE_DRIVER = 'driver'

VEHICLE_ORDER_EMPLOYEE_TYPES = (
    (VEHICLE_ORDER_EMPLOYEE_TYPE_CREATOR, 'Заказчик'),
    (VEHICLE_ORDER_EMPLOYEE_TYPE_EXECUTOR, 'Исполнитель'),
    (VEHICLE_ORDER_EMPLOYEE_TYPE_DRIVER, 'Водитель'),
)


class SpecialVehicleType(DateUserMixin):
    parent_type = models.ForeignKey('SpecialVehicleType', on_delete=models.CASCADE, null=True, blank=True,
                                    verbose_name='Родительский тип')
    title = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(verbose_name='Описание', blank=True, default='')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Тип спецтехники'
        verbose_name_plural = 'Типы спецтехники'
        db_table = 'special_vehicle_type'


class SpecialVehicle(DateUserMixin):
    special_vehicle_type = models.ForeignKey(SpecialVehicleType, on_delete=models.CASCADE,
                                             verbose_name='Тип спецтехники')
    partner = models.ForeignKey(Partner, verbose_name='Партнёр', null=True, blank=True, on_delete=models.SET_NULL)
    number = models.CharField(max_length=255, verbose_name='Номер', blank=True, default='')
    brand = models.CharField(max_length=255, verbose_name='Марка', blank=True, default='')
    model = models.CharField(max_length=255, verbose_name='Модель', blank=True, default='')
    year = models.PositiveSmallIntegerField(verbose_name='Год', blank=True, null=True)
    description = models.CharField(max_length=255, verbose_name='Описание', blank=True, default='')
    status = models.CharField(max_length=255, verbose_name='Статус', blank=True, null=True, choices=VEHICLE_STATUSES,
                              default=VEHICLE_STATUS_ACTIVE)
    default_driver_employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, verbose_name='Основной водитель',
                                                null=True, blank=True, related_name='default_driver_employee')
    owner_employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, verbose_name='Собственник',
                                       null=True, blank=True, related_name='owner_employee')

    def __str__(self):
        return f"{self.number} - {self.brand} - {self.model} - {self.year}"

    def is_busy_today(self):
        return self.specialvehicleorder_set.filter(starting_at__lte=datetime.today(),
                                                   ending_at__gte=datetime.today()).exists()

    class Meta:
        db_table = 'special_vehicle'
        verbose_name = 'Спецтехника'
        verbose_name_plural = 'Спецтехника'


class SpecialVehicleDriver(DateUserMixin):
    special_vehicle_type = models.ForeignKey(SpecialVehicleType, on_delete=models.CASCADE,
                                             verbose_name='Тип спецтехники')
    employee = models.ForeignKey(Employee, verbose_name='Работник', null=True, blank=True, on_delete=models.SET_NULL)
    notes = models.CharField(max_length=255, verbose_name='Примечания', blank=True, default='')

    def __str__(self):
        return f"{self.employee} - {self.special_vehicle_type}"

    class Meta:
        db_table = 'special_vehicle_driver'
        verbose_name = 'Водитель'
        verbose_name_plural = 'Водители'


class SpecialVehicleOrder(DateUserMixin):
    project = models.ForeignKey(Project, verbose_name='Проект', null=True, blank=True, on_delete=models.SET_NULL)
    work = models.ForeignKey(Work, verbose_name='Работа', null=True, blank=True, on_delete=models.SET_NULL)
    starting_at = models.DateTimeField(verbose_name='Начало планируемое', blank=True, null=True)
    started_at = models.DateTimeField(verbose_name='Начало фактическое', blank=True, null=True)
    ending_at = models.DateTimeField(verbose_name='Завершение планируемое', blank=True, null=True)
    ended_at = models.DateTimeField(verbose_name='Завершение фактическое', blank=True, null=True)
    special_vehicle_type = models.ForeignKey(SpecialVehicleType, on_delete=models.CASCADE,
                                             verbose_name='Тип спецтехники')
    special_vehicle = models.ForeignKey(SpecialVehicle, on_delete=models.CASCADE,
                                        verbose_name='Спецтехника')
    status = models.CharField(max_length=255, verbose_name='Статус', blank=True, null=True,
                              choices=VEHICLE_ORDER_STATUSES,
                              default=VEHICLE_ORDER_STATUS_CREATED)
    notes = models.CharField(max_length=255, verbose_name='Примечания', blank=True, default='')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cached_value = dict()
        self.cached_value['project'] = self.project.title if self.pk is not None and self.project else None
        self.cached_value['work'] = self.work.title if self.pk is not None and self.work else None
        self.cached_value[
            'starting_at'] = self.starting_at.isoformat() if self.pk is not None and self.starting_at else None
        self.cached_value[
            'started_at'] = self.started_at.isoformat() if self.pk is not None and self.started_at else None
        self.cached_value['ending_at'] = self.ending_at.isoformat() if self.pk is not None and self.ending_at else None
        self.cached_value['ended_at'] = self.ended_at.isoformat() if self.pk is not None and self.ended_at else None
        self.cached_value['special_vehicle_type'] = self.special_vehicle_type.title if self.pk is not None else None
        self.cached_value['special_vehicle'] = self.special_vehicle.__str__() if self.pk is not None and hasattr(self,
                                                                                                                 'special_vehicle') else None
        self.cached_value['status'] = self.status if self.pk is not None and self.status else None
        self.cached_value['notes'] = self.notes if self.pk is not None and self.notes else None

    def calendar_text(self):
        return mark_safe(
            f"<a href={reverse('admin:vehicle_specialvehicleorder_change', args=[str(self.id)])}>{self.special_vehicle.model}</a>")

    def __str__(self):
        return f"{self.project} - {self.work} - {self.special_vehicle_type} - {self.get_status_display()}"

    def special_format(self, value):
        pass

    def save(self, *args, **kwargs):
        add = True if self.pk is None else False
        super().save(*args, **kwargs)
        for k, v in self.cached_value.items():
            svoc = SpecialVehicleOrderChange()
            svoc.special_vehicle_order = self
            if add:
                svoc.old_value = None
            else:
                svoc.old_value = v
            svoc.field = self._meta.get_field(k).verbose_name
            svoc.new_value = getattr(self, k).__str__()
            if svoc.old_value != svoc.new_value:
                svoc.save()

    class Meta:
        db_table = 'special_vehicle_order'
        verbose_name = 'Заказ СпецТехники'
        verbose_name_plural = 'Заказы СпецТехники'


class SpecialVehicleOrderCalendar(SpecialVehicle):
    class Meta:
        verbose_name = 'Календарь занятости спецтранспорта'
        verbose_name_plural = 'Календарь занятости спецтранспорта'
        proxy = True


class SpecialVehicleOrderChange(DateUserMixin):
    special_vehicle_order = models.ForeignKey(SpecialVehicleOrder, on_delete=models.CASCADE,
                                              related_name="change_special_vehicle_order",
                                              verbose_name='Заказ СпецТехники')
    field = models.CharField(max_length=255, verbose_name='Поле')
    old_value = models.CharField(max_length=255, verbose_name='Старое значение', blank=True, null=True)
    new_value = models.CharField(max_length=255, verbose_name='Новое значение', blank=True, null=True)

    def __str__(self):
        return f'{self.special_vehicle_order} - {self.field} - {self.old_value} - {self.new_value}'

    class Meta:
        db_table = 'special_vehicle_order_change'
        verbose_name = 'История заявки'
        verbose_name_plural = 'Истории заявки'


class SpecialVehicleOrderComment(DateUserMixin):
    special_vehicle_order = models.ForeignKey(SpecialVehicleOrder, on_delete=models.CASCADE,
                                              verbose_name='Заказ СпецТехники')
    employee = models.ForeignKey(Employee, verbose_name='Сотрудник', null=True, blank=True, on_delete=models.SET_NULL)
    body = models.TextField(verbose_name='Текст сообщения')

    def __str__(self):
        return f"{self.special_vehicle_order} - {self.employee} - {self.body}"

    class Meta:
        db_table = 'special_vehicle_order_comment'
        verbose_name = 'Комментарий по заявке'
        verbose_name_plural = 'Комментарии по заявке'


class SpecialVehicleOrderEmployee(DateUserMixin):
    special_vehicle_order = models.ForeignKey(SpecialVehicleOrder, on_delete=models.CASCADE,
                                              verbose_name='Заказ СпецТехники')
    employee = models.ForeignKey(Employee, verbose_name='Сотрудник', null=True, blank=True, on_delete=models.SET_NULL)
    type = models.CharField(max_length=255, verbose_name='', choices=VEHICLE_ORDER_EMPLOYEE_TYPES,
                            default=VEHICLE_ORDER_EMPLOYEE_TYPE_CREATOR)

    def __str__(self):
        return f"{self.special_vehicle_order} - {self.employee} - {self.type}"

    class Meta:
        db_table = 'special_vehicle_order_employee'
        verbose_name = ''
        verbose_name_plural = ''


class RegulationsMaintenance(DateUserMixin):
    vehicle = models.ForeignKey(SpecialVehicle, verbose_name='Спецтехника', on_delete=models.CASCADE)
    spare_part_name = models.CharField(max_length=255, verbose_name='Наименование запчасти')
    replacement_date = models.DateField(verbose_name='Дата замены')
    mileage_on_equipment = models.CharField(max_length=128, verbose_name='Пробег на технике')
    spare_part_hours = models.CharField(max_length=128, verbose_name='Моточасы на новую запчасть')
    cost_of_spare_part = models.DecimalField(verbose_name='Стоимость запчасти', max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.vehicle} - {self.spare_part_name} - {self.replacement_date}"

    class Meta:
        db_table = 'regulations_maintenance'
        verbose_name = 'Регламент обслуживания спецтехники'
        verbose_name_plural = 'Регламенты обслуживания спецтехники'
