from django.db import models

from company.models import Company
from core.models import DateUserMixin

PROJECT_STATUS_ACTIVE = 'active'
PROJECT_STATUS_INACTIVE = 'inactive'
PROJECT_STATUSES = (
    (PROJECT_STATUS_ACTIVE, 'Активно'),
    (PROJECT_STATUS_INACTIVE, 'Не активно'),
)


class Project(DateUserMixin):
    title = models.CharField(max_length=255, verbose_name="Название")
    status = models.CharField(max_length=16, verbose_name="Статус", choices=PROJECT_STATUSES,
                              default=PROJECT_STATUS_ACTIVE)
    color = models.CharField(max_length=16, verbose_name="Цвет")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="Компания", null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'project'
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'


class Work(DateUserMixin):
    project = models.ForeignKey(Project, verbose_name='Проект', on_delete=models.CASCADE)
    title = models.CharField(max_length=255, verbose_name="Название")
    started_at = models.DateTimeField(verbose_name='Дата начала')
    ended_at = models.DateTimeField(verbose_name='Дата завершения', null=True, blank=True)
    notes = models.TextField(verbose_name='Примечание', blank=True)
    color = models.CharField(max_length=16, verbose_name="Цвет")

    def __str__(self):
        return f'{self.title} - {self.started_at}'

    class Meta:
        db_table = 'work'
        verbose_name = 'Работа'
        verbose_name_plural = 'Работы'


class Partner(DateUserMixin):
    title = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(verbose_name='Описание', blank=True)

    def __str__(self):
        return f'{self.title}'

    class Meta:
        db_table = 'partner'
        verbose_name = 'Партнёр'
        verbose_name_plural = 'Партнёры'
