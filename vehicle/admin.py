from datetime import date, timedelta, datetime

from django.contrib import admin
from django.db.models import Q
from django.urls import reverse
from django.utils.safestring import mark_safe

from core.admin import VektorAdmin, PassThroughFilter
from core.utils import last_day
from vehicle.models import SpecialVehicleType, SpecialVehicle, SpecialVehicleDriver, SpecialVehicleOrder, \
    SpecialVehicleOrderChange, SpecialVehicleOrderCalendar, VEHICLE_STATUS_DELETED, RegulationsMaintenance
from vehicle.forms import VehicleOrderCreateForm, VehicleOrderChangeForm


class SpecialVehicleOwnerFilter(admin.SimpleListFilter):
    title = 'Собственник'
    parameter_name = 'owner_employee'

    def lookups(self, request, model_admin):
        owners = set([obj.owner_employee for obj in model_admin.model.objects.filter(owner_employee__isnull=False)])
        return [(owner.id, owner.__str__) for owner in owners]

    def queryset(self, request, queryset):
        # Apply the selected filter
        if self.value():
            return queryset.filter(owner_employee=self.value())
        else:
            return queryset


class SpecialVehicleDriverInline(admin.TabularInline):
    model = SpecialVehicleDriver
    readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by')
    extra = 1


@admin.register(SpecialVehicleType)
class SpecialVehicleTypeAdmin(VektorAdmin):
    search_fields = ['title', 'description']
    list_display = ('parent_type', 'title', 'description')
    list_display_links = ('parent_type', 'title')
    readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by')
    inlines = [SpecialVehicleDriverInline]
    autocomplete_fields = ['parent_type']


@admin.register(SpecialVehicle)
class SpecialVehicleAdmin(VektorAdmin):
    list_display = (
        'special_vehicle_type', 'partner', 'owner_employee', 'number', 'brand', 'model', 'year', 'description',
        'created_at', 'status')
    search_fields = (
        'special_vehicle_type__title', 'number', 'brand', 'model', 'year', 'description',
        'created_at', 'status')
    readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by')
    list_filter = ('status', SpecialVehicleOwnerFilter, 'special_vehicle_type',)
    autocomplete_fields = ['special_vehicle_type', 'default_driver_employee', 'owner_employee']


class SpecialVehicleOrderChangInlineAdmin(admin.TabularInline):
    model = SpecialVehicleOrderChange
    readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by', 'special_vehicle_order',
                       'field', 'old_value', 'new_value')
    extra = 0
    can_delete = False


@admin.register(SpecialVehicleOrder)
class SpecialVehicleOrderAdmin(VektorAdmin):
    list_display = ('status', 'starting_at', 'project_title', 'work_title')
    list_display_links = ('status', 'starting_at', 'project_title', 'work_title')
    readonly_fields = ['created_at', 'created_by', 'updated_at', 'updated_by']
    ordering = ['-id']
    inlines = [SpecialVehicleOrderChangInlineAdmin]
    add_form = VehicleOrderCreateForm
    form = VehicleOrderChangeForm
    autocomplete_fields = ['special_vehicle', 'special_vehicle_type', 'project', 'work']

    def get_form(self, request, obj=None, change=False, **kwargs):

        defaults = {}
        if obj is None:
            defaults['form'] = self.add_form
            self.readonly_fields = ['created_at', 'created_by', 'updated_at', 'updated_by']
        else:
            self.readonly_fields += ['project', 'work', 'starting_at', 'ending_at', 'special_vehicle_type', 'special_vehicle']
        defaults.update(kwargs)
        form = super().get_form(request, obj, change, **defaults)
        vehicle = SpecialVehicle.objects.filter(id=request.GET.get('vehicle_id', None)).first()
        if vehicle:
            form.base_fields['starting_at'].initial = datetime.now()
            form.base_fields['special_vehicle'].initial = vehicle.id
            form.base_fields['special_vehicle_type'].initial = vehicle.special_vehicle_type_id

        return form

    def project_title(self, obj):
        if obj.project:
            return obj.project.title
        return '-'

    project_title.short_description = 'Проект'

    def work_title(self, obj):
        if obj.work:
            return obj.work.title
        return '-'
    work_title.short_description = 'Работа'

    class Media:
        js = ('vehicle/js/vehicle.js',)


class VehicleInOrderFilterAdmin(admin.SimpleListFilter):
    title = 'В заказе'
    parameter_name = 'starting_at'
    date_first = None

    def lookups(self, request, model_admin):
        return [
            ('free_today', 'Свободные сегодня'),
            ('in_order', 'В заказе на данный месяц'),
            ('out_order', 'Без заказов на данный месяц'),
        ]

    def queryset(self, request, queryset, VEHICLE_STATUS_NONE=None):
        self.date_first = request.GET.get('day__gte', self.date_first)
        if self.date_first:
            self.date_first = date.fromisoformat(self.date_first)
            date_first = date(self.date_first.year, self.date_first.month, 1)
            last_month_day = last_day(self.date_first.year, self.date_first.month)
            last = date(self.date_first.year, self.date_first.month, last_month_day)
        else:
            date_first = date(date.today().year, date.today().month, 1)
            last_month_day = last_day(date.today().year, date.today().month)
            last = date(date.today().year, date.today().month, last_month_day)
        queryset = queryset.exclude(status=VEHICLE_STATUS_DELETED)
        ids_in = SpecialVehicleOrder.objects.filter(starting_at__gte=date_first,
                                                    starting_at__lte=last).values_list('special_vehicle_id',
                                                                                       flat=True)
        if self.value() == 'in_order':
            return queryset.filter(id__in=ids_in)
        if self.value() == 'out_order':
            return queryset.exclude(id__in=ids_in)
        if self.value() == 'free_today':
            free_today = date.today()
            ids_free = SpecialVehicleOrder.objects.filter(starting_at__lte=free_today,
                                                          ending_at=free_today).values_list('special_vehicle_id',
                                                                                            flat=True)
            return queryset.exclude(id__in=ids_free)
        return queryset


@admin.register(SpecialVehicleOrderCalendar)
class SpecialVehicleOrderCalendarAdmin(admin.ModelAdmin):
    change_list_template = 'admin/vehicle/_month_table.html'
    list_display = ('number', 'model', 'special_vehicle_type', 'get_create_order', 'is_free')
    list_display_links = ('number', 'model')
    after_day = None
    list_filter = (VehicleInOrderFilterAdmin, )

    @admin.display(empty_value="-", description='Создать заказ')
    def get_create_order(self, obj):
        return mark_safe(f"<a href={reverse('admin:vehicle_specialvehicleorder_add')}?vehicle_id={obj.pk}>Создать заказ</a>")

    @admin.display(description='Свободен сегодня')
    def is_free(self, obj):
        return not obj.is_busy_today()
    is_free.boolean = True

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        after_day = request.GET.get('day__gte', self.after_day)
        if not after_day:
            d = date.today()
        else:
            try:
                self.after_day = after_day
                split_after_day = after_day.split('-')
                d = date(year=int(split_after_day[0]), month=int(split_after_day[1]), day=1)
            except Exception as e:
                d = date.today()

        previous_month = date(year=d.year, month=d.month, day=1)
        previous_month = previous_month - timedelta(days=1)
        previous_month = date(year=previous_month.year, month=previous_month.month, day=1)

        first_day = date(d.year, d.month, 1)
        last = last_day(d.year, d.month)
        next_month = date(year=d.year, month=d.month, day=last)
        next_month = next_month + timedelta(days=1)
        next_month = date(year=next_month.year, month=next_month.month, day=1)

        extra_context['previous_month'] = reverse(
            'admin:vehicle_specialvehicleordercalendar_changelist') + '?day__gte=' + str(
            previous_month)
        extra_context['next_month'] = reverse(
            'admin:vehicle_specialvehicleordercalendar_changelist') + '?day__gte=' + str(next_month)

        from core.utils import EventCalendar
        qs = list(SpecialVehicleOrder.objects.select_related('special_vehicle').filter(starting_at__gte=first_day))
        days = {}
        for q in qs:
            day = q.starting_at.day
            ending_day = q.ending_at.day if q.ending_at.date() <= next_month else date(year=d.year, month=d.month,
                                                                                       day=last).day
            while day <= ending_day:
                if day not in days:
                    days[day] = []
                days[day].append(q)
                day += 1

        cal = EventCalendar(events=days)
        html_calendar = cal.formatmonth(d.year, d.month, withyear=True)
        html_calendar = html_calendar.replace('<td ', '<td  width="150" height="150"')
        extra_context['calendar'] = html_calendar
        return super(SpecialVehicleOrderCalendarAdmin, self).changelist_view(request, extra_context)


@admin.register(RegulationsMaintenance)
class RegulationsMaintenanceAdmin(VektorAdmin):
    list_display = ('vehicle', 'spare_part_name', 'replacement_date', 'mileage_on_equipment', 'spare_part_hours', 'cost_of_spare_part')
    list_display_links = ('vehicle', 'spare_part_name',)
    readonly_fields = ['created_at', 'created_by', 'updated_at', 'updated_by']
    search_fields = ('vehicle', 'spare_part_name', 'replacement_date', 'mileage_on_equipment')
    autocomplete_fields = ['vehicle', ]
