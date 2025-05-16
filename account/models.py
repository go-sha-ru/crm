from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.safestring import mark_safe

from core.models import DateUserMixin


class VectorUser(AbstractUser):
    patronymic = models.CharField(max_length=255, blank=True, verbose_name="Отчество")
    date_of_birth = models.DateField(verbose_name='Дата рождения', blank=True, null=True)
    phone = models.CharField(max_length=255, verbose_name='Телефон', blank=True, default='')

    def fio(self):
        s = f"{self.last_name}"
        if self.first_name:
            s += f'&nbsp;{self.first_name[0].upper()}.'
        if self.patronymic:
            s += f'&nbsp;{self.patronymic[0].upper()}.'
        return mark_safe(s)

    def __str__(self):
        ret = f'({self.username}) {self.fio()}'
        return mark_safe(ret)


ROLE_STATUS_ACTIVE = 'active'
ROLE_STATUS_INACTIVE = 'inactive'
ROLE_STATUSES = (
    (ROLE_STATUS_ACTIVE, 'Активно'),
    (ROLE_STATUS_INACTIVE, 'Не активно'),
)


class Role(DateUserMixin):
    title = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(verbose_name="Описание", blank=True, default='')
    status = models.CharField(max_length=16, verbose_name="Статус", choices=ROLE_STATUSES, default=ROLE_STATUS_ACTIVE)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Должность'
        verbose_name_plural = 'Должности'
        db_table = 'role'


class YiiUser(DateUserMixin):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    username = models.CharField(max_length=255, verbose_name='Лошин')
    surname = models.CharField(max_length=255, verbose_name='Фамилия')
    firstname = models.CharField(max_length=255, verbose_name='Имя')
    patronymic = models.CharField(max_length=255, verbose_name='Отчество')
    date_of_birth = models.DateField(verbose_name='Дата рождения')
    status = models.CharField(max_length=255, verbose_name='Статус')

    def __str__(self):
        return f'{self.surname} {self.firstname} {self.patronymic}'

    class Meta:
        db_table = 'user'
        verbose_name = 'Yii пользователь'
        verbose_name_plural = 'Yii пользователь'


class YiiUserContact(DateUserMixin):
    user = models.ForeignKey(YiiUser, related_name='contacts', on_delete=models.CASCADE)
    type = models.CharField(max_length=16, verbose_name='Тип')
    value = models.CharField(max_length=255, verbose_name='Значение')
    description = models.TextField(max_length=255, verbose_name='Описание', blank=True, default='')
    status = models.CharField(max_length=255, verbose_name='Статус')

    def __str__(self):
        return f'{self.user} - {self.type}: {self.value}'

    class Meta:
        db_table = 'user_contact'
        verbose_name = 'Yii контакт пользователя'
        verbose_name_plural = 'Yii контакты пользователей'


class RolePermission(DateUserMixin):
    SUPER_USER = 'super_user'
    ROLE_EDIT = 'role_edit'
    USER_ROLE_PERMISSION_EDIT = 'user_role_permission_edit'
    USER_LIST = 'user_list'
    USER_VIEW = 'user_view'
    USER_EDIT = 'user_edit'
    COMPANY_FULL = 'company_full'
    EMPLOYEE_LIST = 'employee_list'
    EMPLOYEE_VIEW = 'employee_view'
    EMPLOYEE_EDIT = 'employee_edit'
    EMPLOYEE_RATE_EDIT = 'employee_rate_edit'
    EMPLOYEE_TIME_FULL = 'employee_time_full'
    EMPLOYEE_WORK_ITEM_FULL = 'employee_work_item_full'
    EMPLOYEE_CREDIT = 'employee_credit'
    PROJECT_FULL = 'project_full'
    PROJECT_LIST = 'project_list'
    PROJECT_VIEW = 'project_view'
    PROJECT_EDIT = 'project_edit'
    PARTNER_VIEW = 'partner_view'
    PARTNER_EDIT = 'partner_edit'
    SALARY_FULL = 'salary_full'
    SALARY_EMPLOYEE_LIST = 'salary_employee_list'
    SALARY_EMPLOYEE_VIEW = 'salary_employee_view'
    SALARY_EMPLOYEE_SELF_VIEW = 'salary_employee_self_view'
    SALARY_TYPE_GROUP_EDIT = 'salary_type_group_edit'
    SPECIAL_VEHICLE_TYPE_EDIT = 'special_vehicle_type_edit'
    SPECIAL_VEHICLE_EDIT = 'special_vehicle_edit'
    SPECIAL_VEHICLE_DRIVER_EDIT = 'special_vehicle_driver_edit'
    SPECIAL_VEHICLE_ORDER_LIST = 'special_vehicle_order_list'
    SPECIAL_VEHICLE_ORDER_VIEW = 'special_vehicle_order_view'
    SPECIAL_VEHICLE_ORDER_ADD = 'special_vehicle_order_add'
    SPECIAL_VEHICLE_ORDER_EXECUTE = 'special_vehicle_order_execute'
    SPECIAL_VEHICLE_ORDER_COMMENT = 'special_vehicle_order_comment'
    SPECIAL_VEHICLE_ORDER_CHANGES_VIEW = 'special_vehicle_order_changes_view'
    SPECIAL_VEHICLE_ORDER_CHAT_VIEW = 'special_vehicle_order_chat_view'
    SPECIAL_VEHICLE_ORDER_CHAT_PARTICIPANTS = 'special_vehicle_order_chat_participants'
    WORK_FULL = 'work_full'
    WORK_LIST = 'work_list'
    WORK_EDIT = 'work_edit'
    WORK_VIEW = 'work_view'

    ROLE_PERMISSIONS = (
        (SUPER_USER, 'Администратор'),
        (ROLE_EDIT, 'Управление должностями'),
        (USER_ROLE_PERMISSION_EDIT, 'Управление правами доступа'),
        (USER_LIST, 'Пользователи (список)'),
        (USER_VIEW, 'Пользователи (просмотр)'),
        (USER_EDIT, 'Пользователи (изменение)'),
        (COMPANY_FULL, 'Компании'),
        (EMPLOYEE_LIST, 'Работники (список)'),
        (EMPLOYEE_VIEW, 'Работники (просмотр)'),
        (EMPLOYEE_EDIT, 'Работники (изменение)'),
        (EMPLOYEE_RATE_EDIT, 'Работники (зарплата)'),
        (EMPLOYEE_CREDIT, 'Кредиты'),
        (EMPLOYEE_TIME_FULL, 'Рабочее время (полный доступ)'),
        (EMPLOYEE_WORK_ITEM_FULL, 'Сдельная работа (польный доступ)'),
        (PROJECT_FULL, 'Проекты (полный доступ)'),
        (PROJECT_LIST, 'Проекты (список)'),
        (PROJECT_VIEW, 'Проекты (просмотр)'),
        (PROJECT_EDIT, 'Проекты (изменение)'),
        (PARTNER_EDIT, 'Партнеры (изменение)'),
        (PARTNER_VIEW, 'Партнеры (просмотр)'),
        (SALARY_FULL, 'Зарплата (полный доступ)'),
        (SALARY_EMPLOYEE_LIST, 'Зарплата (список работников)'),
        (SALARY_EMPLOYEE_VIEW, 'Зарплата (просмотр по работнику)'),
        (SALARY_EMPLOYEE_SELF_VIEW, 'Зарплата (просмотр собственной)'),
        (SALARY_TYPE_GROUP_EDIT, 'Зарплата (управление группировкой по типам)'),
        (SPECIAL_VEHICLE_EDIT, 'Спецтехника (изменение)'),
        (SPECIAL_VEHICLE_TYPE_EDIT, 'Спецтехника типы (изменение)'),
        (SPECIAL_VEHICLE_DRIVER_EDIT, 'Спецтехника водители (изменение)'),
        (SPECIAL_VEHICLE_ORDER_ADD, 'Спецтехника заявки (создание)'),
        (SPECIAL_VEHICLE_ORDER_LIST, 'Спецтехника заявки (список)'),
        (SPECIAL_VEHICLE_ORDER_VIEW, 'Спецтехника заявки (просмотр)'),
        (SPECIAL_VEHICLE_ORDER_EXECUTE, 'Спецтехника заявки (выполнение)'),
        (SPECIAL_VEHICLE_ORDER_COMMENT, 'Спецтехника заявки (комментирование)'),
        (SPECIAL_VEHICLE_ORDER_CHANGES_VIEW, 'Спецтехника заявки (просмотр изменений)'),
        (SPECIAL_VEHICLE_ORDER_CHAT_VIEW, 'Спецтехника заявки (просмотр чата)'),
        (SPECIAL_VEHICLE_ORDER_CHAT_PARTICIPANTS, 'Спецтехника заявки (участие в чате)'),
        (WORK_FULL, 'Работы (полный доступ)'),
        (WORK_LIST, 'Работы (список)'),
        (WORK_VIEW, 'Работы (просмотр)'),
        (WORK_EDIT, 'Работы (изменение)'),
    )
    role = models.ForeignKey(Role, on_delete=models.CASCADE, verbose_name='Роль')
    permission = models.CharField(max_length=255, verbose_name='Разрешения', choices=ROLE_PERMISSIONS)
    entity_based = models.BooleanField(default=False, verbose_name='На основе сущности')

    def __str__(self):
        return f'{self.role} {self.get_permission_display()}'

    class Meta:
        db_table = 'role_permission'
        verbose_name = 'Разрешение роли'
        verbose_name_plural = 'Разрешения роли'


class UserPermissionEntity(DateUserMixin):
    user = models.ForeignKey(VectorUser, on_delete=models.CASCADE, verbose_name='Пользователь')
    role_permission = models.ForeignKey(RolePermission, on_delete=models.CASCADE, verbose_name='Разрешение роли')
    entity_class = models.CharField(max_length=255, verbose_name='Класс')
    entity_id = models.IntegerField(verbose_name='Id объекта')

    @property
    def get_model(self):
        model_name = self.entity_class.split('\\')[-1].lower()
        ct = ContentType.objects.get(model=model_name)
        model = ct.model_class()
        return model

    @property
    def entity_object(self):
        model = self.get_model
        obj = model.objects.get(pk=self.entity_id)
        return obj

    class Meta:
        db_table = 'user_permission_entity'
        verbose_name = 'Сущность разрешения пользователя'
        verbose_name_plural = 'Сущность разрешения пользователя'
