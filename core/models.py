from django.conf import settings
from django.db import models


class DateUserMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   verbose_name='Создано пользователем',
                                   on_delete=models.CASCADE,
                                   null=True, blank=True,
                                   db_column='created_by',
                                   related_name="+")
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   verbose_name='Изменено пользователем',
                                   on_delete=models.CASCADE,
                                   null=True, blank=True,
                                   db_column='updated_by',
                                   related_name="+")

    class Meta:
        abstract = True
