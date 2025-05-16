from django.contrib import admin


class VektorAdmin(admin.ModelAdmin):
    list_per_page = 25
    readonly_fields = ['created_at', 'created_by', 'updated_at', 'updated_by']

    def save_model(self, request, obj, form, change):
        if obj:
            if not obj.id:
                obj.created_by = request.user
            else:
                obj.updated_by = request.user
        super().save_model(request, obj, form, change)


class PassThroughFilter(admin.SimpleListFilter):
    title = ''
    parameter_names = ['date', 'day__gte']
    parameter_name = 'date'
    template = 'admin/core/hidden_filter.html'

    def lookups(self, request, model_admin):
        ret = []
        for parameter_name in self.parameter_names:
            self.parameter_name = parameter_name
            ret.append((request.GET.get(parameter_name), ''))
        return ret

    def queryset(self, request, queryset):
        return queryset
