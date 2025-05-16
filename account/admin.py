from django.utils.safestring import mark_safe
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from account.models import Role, VectorUser, RolePermission, UserPermissionEntity
from core.admin import VektorAdmin
from employee.models import EmployeeGroup


@admin.register(VectorUser)
class UserAdminConfig(UserAdmin):
    model = VectorUser
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )


@admin.register(Role)
class RoleAdmin(VektorAdmin):
    list_display = ('title', 'description', 'status')
    search_fields = ('title', 'description', 'status')
    readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by')
    ordering = ('id', )
    list_filter = ('status',)


@admin.register(RolePermission)
class RolePermissionAdmin(VektorAdmin):
    list_display = ('role', 'permission', 'entity_based')
    ordering = ['role__title']


class UserPermissionEntityFilter(admin.SimpleListFilter):
    title = "Объект"
    parameter_name = 'entity_id'

    def lookups(self, request, model_admin):
        items = EmployeeGroup.objects.values_list('id', 'title')
        ret = []
        for item in items:
            ret.append((item[0], item[1]))
        return ret

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(entity_id=self.value())
        return queryset


@admin.register(UserPermissionEntity)
class UserPermissionEntityAdmin(VektorAdmin):
    list_display = ('user_fio', 'role_permission', 'get_model', 'entity_object')
    ordering = ['user__last_name', 'user__first_name']
    list_filter = [
        UserPermissionEntityFilter,
        ("user", admin.RelatedOnlyFieldListFilter),
    ]

    @admin.display(empty_value='-')
    def user_fio(self, obj):
        ret = f'({obj.user.username}) {obj.user.fio()}'
        return mark_safe(ret)
    user_fio.short_description = 'ФИО'

    @admin.display(empty_value='-')
    def get_model(self, obj):
        model = obj.get_model
        return model._meta.verbose_name.title()
    get_model.short_description = 'Тип'

    @admin.display(empty_value='-')
    def entity_object(self, obj):
        return obj.entity_object
    entity_object.short_description = 'Объект'

