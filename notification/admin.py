from django.contrib import admin
from django.contrib.admin import SimpleListFilter

from core.admin import VektorAdmin
from employee.models import Employee
from notification.models import Notification, NotificationEvent, NotificationTemplate


@admin.register(NotificationEvent)
class NotificationEventAdmin(VektorAdmin):
    list_display = ('keyword', 'status')


@admin.register(NotificationTemplate)
class NotificationEventAdmin(VektorAdmin):
    list_display = ('notification_event', 'type', 'status', 'subject')


@admin.register(Notification)
class NotificationAdmin(VektorAdmin):
    list_display = ('recipient', 'status', 'subject')
    ordering = ['-created_at']

    def has_change_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # if request.user.is_superuser:
        #     return qs
        return qs.filter(recipient__in=[request.user])
