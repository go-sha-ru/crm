from django.conf import settings
from django.db import models

from core.models import DateUserMixin

NOTIFICATION_STATUS_ACTIVE = 'active'
NOTIFICATION_STATUS_DELETED = 'deleted'

NOTIFICATION_STATUSES = (
    (NOTIFICATION_STATUS_ACTIVE, 'Активный'),
    (NOTIFICATION_STATUS_DELETED, 'Удалённый'),
)

NOTIFICATION_TYPE_WEB = 'web'
NOTIFICATION_TYPE_PUSH = 'push'
NOTIFICATION_TYPE_EMAIL = 'email'
NOTIFICATION_TYPE_TELEGRAM = 'telegram'

NOTIFICATION_TYPES = (
    (NOTIFICATION_TYPE_WEB, 'Web'),
    (NOTIFICATION_TYPE_PUSH, 'Push'),
    (NOTIFICATION_TYPE_EMAIL, 'Email'),
    (NOTIFICATION_TYPE_TELEGRAM, 'Telegram'),
)

NOTIFICATION_DELIVERY_STATUS_SENT = 'sent'
NOTIFICATION_DELIVERY_STATUS_READ = 'read'
NOTIFICATION_DELIVERY_STATUS_DELETED = 'deleted'
NOTIFICATION_DELIVERY_STATUS_BLOCKED = 'blocked'
NOTIFICATION_DELIVERY_STATUS_INACTIVE = 'inactive'

NOTIFICATION_DELIVERY_STATUSES = (
    (NOTIFICATION_DELIVERY_STATUS_SENT, 'Отправлено'),
    (NOTIFICATION_DELIVERY_STATUS_READ, 'Прочитано'),
    (NOTIFICATION_DELIVERY_STATUS_DELETED, 'Удалено'),
    (NOTIFICATION_DELIVERY_STATUS_BLOCKED, 'Заблокировано'),
    (NOTIFICATION_DELIVERY_STATUS_INACTIVE, 'Неактивно'),
)


class NotificationEvent(DateUserMixin):
    keyword = models.CharField(max_length=64, verbose_name="Слова")
    status = models.CharField(max_length=64, verbose_name="Статус", choices=NOTIFICATION_STATUSES,
                              default=NOTIFICATION_STATUS_ACTIVE)

    def __str__(self):
        return f"{self.keyword}: {self.status}"

    class Meta:
        db_table = 'notification_event'
        verbose_name = 'Событие уведомления'
        verbose_name_plural = 'События уведомления'


class NotificationTemplate(DateUserMixin):
    notification_event = models.ForeignKey(NotificationEvent, on_delete=models.CASCADE,
                                           verbose_name='Событие уведомления')
    type = models.CharField(max_length=16, verbose_name='Тип', choices=NOTIFICATION_TYPES,
                            default=NOTIFICATION_TYPE_WEB)
    status = models.CharField(max_length=64, verbose_name="Статус", choices=NOTIFICATION_STATUSES,
                              default=NOTIFICATION_STATUS_ACTIVE)
    subject = models.TextField(verbose_name='Тема')
    content = models.TextField(verbose_name='Содержимое')

    def __str__(self):
        return f"{self.notification_event}: {self.type}: {self.subject}"

    class Meta:
        db_table = 'notification_template'
        verbose_name = 'Шаблон уведомления'
        verbose_name_plural = 'Шаблоны уведомлений'


class Notification(DateUserMixin):
    notification_template = models.ForeignKey(NotificationTemplate, on_delete=models.CASCADE,
                                              verbose_name='Шаблон уведомления')
    status = models.CharField(max_length=255, verbose_name='Статус', choices=NOTIFICATION_DELIVERY_STATUSES,
                              default=NOTIFICATION_DELIVERY_STATUS_SENT)
    model_class = models.CharField(max_length=255, verbose_name='Класс модели')
    model_id = models.IntegerField(verbose_name='ID модели')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='ID Получателя', on_delete=models.SET_NULL,
                                  related_name='recipient', null=True, blank=True)
    recipient_to = models.CharField(max_length=255, verbose_name='Получатель', null=True, blank=True)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='ID Отправителя', null=True, blank=True,
                               on_delete=models.SET_NULL, related_name='sender')
    sent_from = models.CharField(max_length=255, verbose_name='Отправитель', null=True, blank=True)
    subject = models.TextField(verbose_name='Тема')
    content = models.TextField(verbose_name='Содержимое')
    error = models.TextField(verbose_name='Ошибка', null=True, blank=True)
    data = models.JSONField(verbose_name='JSON данные')

    def __str__(self):
        return f"{self.model_class}: {self.status}"

    class Meta:
        db_table = 'notification'
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
