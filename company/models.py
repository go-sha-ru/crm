from django.db import models

from core.models import DateUserMixin


class Company(DateUserMixin):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    STATUS_CHOICES = (
        (ACTIVE, 'Активный'),
        (INACTIVE, 'Не активный'),
    )
    title = models.CharField(max_length=255, verbose_name="Название", blank=True)
    inn = models.CharField(max_length=255, verbose_name="ИНН", blank=True)
    legal_address = models.CharField(max_length=255, verbose_name="Юридический адрес", blank=True)
    basis_title = models.CharField(max_length=255, verbose_name="Основание", blank=True)
    director = models.CharField(max_length=255, verbose_name="Директор", blank=True)
    notes = models.TextField(blank=True, verbose_name="Примечание")
    status = models.CharField(max_length=16, verbose_name="Статус", choices=STATUS_CHOICES, default=ACTIVE)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Компания"
        verbose_name_plural = "Компании"
        db_table = f"company"
