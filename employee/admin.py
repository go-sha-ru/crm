import decimal
from datetime import datetime, date

from django.contrib import admin, messages
from django.contrib.admin import SimpleListFilter
from django.http import HttpResponseRedirect, QueryDict
from django.urls import reverse, path

from core.admin import VektorAdmin, PassThroughFilter
from core.utils import last_day, add_months
from employee.forms import SalaryForm, SalaryViewForm, EmployeeGroupForm, SalaryUploadForm, SalaryEmployeeItemForm, \
    EmployeeWorkTimeHeader, EmployeeCreditForm, EmployeeWorkMassTime, EmployeeWorkMassWorkForm
from employee.models import Employee, EmployeeGroup, EMPLOYEE_STATUS_ACTIVE, SalaryView, Salary, SalaryEmployee, \
    EMPLOYEE_STATUS_FIRED, SalaryTypeGroup, SalaryEmployeeItem, EmployeeWorkTime, EmployeeTransfer, EmployeeTime, \
    EmployeeJobTime, EmployeeWorkItem, EmployeeCredit, EmployeeCreditPayment
from employee.views import MassEmployeeWorkTimeView


@admin.action(description="Перевести из уволенных в активные")
def make_active(modeladmin, request, queryset):
    queryset.update(status=EMPLOYEE_STATUS_ACTIVE)


@admin.register(Employee)
class EmployeeAdmin(VektorAdmin):
    list_display = ('role', 'employee_group', 'user', '__str__', 'employment_date', 'dismissal_date', 'status')
    search_fields = ('surname', 'firstname', 'patronymic')
    readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by')
    ordering = ('surname', 'firstname', 'patronymic')
    list_filter = ('status', 'employee_group')
    actions = [make_active, ]
    autocomplete_fields = ['employee_group', 'role']

    def changelist_view(self, request, extra_context=None):
        if not request.GET.get('status__exact'):
            q = request.GET.copy()
            q['status__exact'] = EMPLOYEE_STATUS_ACTIVE
            request.GET = q
            request.META['QUERY_STRING'] = request.GET.urlencode()
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(EmployeeTransfer)
class EmployeeTransferAdmin(VektorAdmin):
    list_display = ('fio', 'date_from', 'employee_group_from', 'employee_group_to')
    search_fields = ('employee__surname', 'employee__firstname', 'employee__patronymic')
    readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by', 'employee_group_from')
    autocomplete_fields = ['employee', 'employee_group_from', 'employee_group_to']

    def save_model(self, request, obj, form, change):
        obj.employee_group_from = obj.employee.employee_group
        obj.employee.employee_group = obj.employee_group_to
        obj.employee.save()
        super().save_model(request, obj, form, change)


class EmployeeInlineAdmin(admin.TabularInline):
    model = Employee
    extra = 0
    fields = ['role', 'employee_group', 'surname', 'firstname', 'patronymic', 'employment_date', 'dismissal_date']


@admin.register(EmployeeGroup)
class EmployeeGroupAdmin(VektorAdmin):
    list_display = ('title',)
    search_fields = ('title',)
    readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by')
    inlines = [EmployeeInlineAdmin]


@admin.register(SalaryView)
class SalaryViewAdmin(admin.ModelAdmin):
    list_display = ('title', 'show_time_column', 'show_total_column')


@admin.register(Salary)
class SalaryAdmin(VektorAdmin):
    form = SalaryForm
    fieldsets = [
        (None, {'fields': [('date_first_day', 'date_last_day', 'work_hours'), 'notes']}),
    ]
    actions = None

    def response_change(self, request, obj):
        if "_calc" in request.POST:
            ret = obj.calculate_salary()
            if ret:
                self.message_user(request, "Расчёт произведён", messages.SUCCESS)
            else:
                self.message_user(request, 'Ошибка расчета.', messages.ERROR)
            return HttpResponseRedirect(".")
        if "_move_next" in request.POST:
            obj.move_next()
            self.message_user(request, 'Остатки перенесены на следующий месяц.', messages.SUCCESS)
            return HttpResponseRedirect(".")
        if "_upload" in request.POST:
            form = SalaryUploadForm(request.POST, request.FILES)
            if form.is_valid():
                success, errors = form.upload_salary(obj)
                for suc in success:
                    self.message_user(request, f'Данные файла {suc} успешно загружены.', messages.SUCCESS)
                for f_name, error in errors.items():
                    for text in error:
                        self.message_user(request, f'В файле {f_name} ошибка {text}.', messages.ERROR)
            return HttpResponseRedirect(".")
        return super(SalaryAdmin, self).response_change(request, obj)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = {'show_save_and_continue': False, 'show_save_and_add_another': False, 'show_delete': False}
        if object_id:
            extra_context['upload_form'] = SalaryUploadForm()
            extra_context['salary_view'] = request.GET.get('salary_view', 1)
            extra_context['employee_group'] = request.GET.get('employee_group', None)
            sed = {}
            salary_employees = {}
            prev_se = None
            salary = Salary.objects.get(pk=object_id)
            salary_view = SalaryView.objects.get(pk=extra_context['salary_view'])
            salary_employee = SalaryEmployee.objects.prefetch_related('salary').filter(
                salary_id=object_id).order_by('employee__employee_group_id')
            employees = Employee.objects.order_by('employee_group_id', 'surname',
                                                  'firstname')

            if extra_context['employee_group']:
                salary_employee = salary_employee.filter(
                    employee__employee_group_id=extra_context['employee_group'])
                employees = employees.filter(employee_group_id=extra_context['employee_group'])

            total_amounts = {}
            amount_all = 0
            for se in salary_employee:
                se.set_total_amount_by_group(salary_view.pk)
                se.set_total_amount()
                for k, v in se.total_amount.items():
                    if k not in total_amounts:
                        total_amounts[k] = 0
                    total_amounts[k] += v if v is not None else 0
                amount_all += se.amount_all
                salary_employees[se.employee_id] = se

            for empl in employees:
                if not prev_se or prev_se.employee_group_id != empl.employee_group_id:
                    sed[empl.employee_group.title] = []
                    prev_se = empl
                if empl.status == EMPLOYEE_STATUS_FIRED and empl.dismissal_date > salary.date_first_day:
                    if empl.id not in salary_employees:
                        se = SalaryEmployee(employee_id=empl.id, salary_id=object_id)
                    else:
                        se = salary_employees[empl.id]
                    sed[empl.employee_group.title].append(se)
                elif empl.status == EMPLOYEE_STATUS_ACTIVE and empl.employment_date <= salary.date_last_day:
                    if empl.id not in salary_employees:
                        se = SalaryEmployee(employee_id=empl.id, salary_id=object_id)
                    else:
                        se = salary_employees[empl.id]
                    sed[empl.employee_group.title].append(se)

            extra_context['employee_group_form'] = EmployeeGroupForm(initial=request.GET)
            extra_context['salary_view_form'] = SalaryViewForm(initial=request.GET)
            extra_context['salary_type_groups'] = SalaryTypeGroup.objects.filter(
                salary_view_id=extra_context['salary_view']
            )
            extra_context['salary_view'] = salary_view
            extra_context['sed'] = sed
            extra_context['total_amounts'] = total_amounts
            extra_context['amount_all'] = amount_all
            extra_context['salary'] = salary
            self.change_form_template = 'admin/employee/salary_change_list.html'
        return super(SalaryAdmin, self).changeform_view(request, object_id, extra_context=extra_context)

    class Media:
        css = {all: ('employee/css/employee.css',)}
        js = ('employee/js/employee.js',)


@admin.register(SalaryEmployeeItem)
class SalaryEmployeeItemAdmin(VektorAdmin):
    form = SalaryEmployeeItemForm
    list_display = ('amount', 'type', 'notes')
    fieldsets = [
        (None, {'fields': [('type', 'date', 'amount'), 'notes']}),
        (None, {'fields': ['employee_id', 'salary_id', 'salary_employee_id']}),
    ]

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super(SalaryEmployeeItemAdmin, self).get_form(request, obj, change, **kwargs)
        group_id = request.GET.get('group_id', None)
        employee_id = request.GET.get('employee_id', None)
        if group_id:
            stg = SalaryTypeGroup.objects.filter(pk=group_id).first()
            if stg:
                form.base_fields['type'].choices = stg.get_items_labels()
        form.base_fields['date'].initial = datetime.today()

        return form

    def save_model(self, request, obj, form, change):
        salary_id = form.cleaned_data['salary_id']
        employee_id = form.cleaned_data['employee_id']
        salary = Salary.objects.get(pk=salary_id)
        salary_employee = salary.get_salary_employee_by_employee(employee_id)
        obj.salary_employee = salary_employee
        super(SalaryEmployeeItemAdmin, self).save_model(request, obj, form, change)

    def has_module_permission(self, request):
        return False


@admin.register(EmployeeWorkTime)
class EmployeeWorkTimeAdmin(admin.ModelAdmin):
    change_list_template = 'admin/employee/work_time.html'
    qs = None
    search_fields = ['employee_group', '']
    list_filter = [PassThroughFilter, ]
    first_date = None
    TimesModel = EmployeeTime
    is_hours = True

    def get_urls(self):
        urls = super().get_urls()
        form = EmployeeWorkMassTime if self.is_hours else EmployeeWorkMassWorkForm

        new_urls = [
            path('mass-time/', MassEmployeeWorkTimeView.as_view(
                model_admin=self,
                model=Employee,
                is_hours=self.is_hours,
                form_class=form), name='mass_time'),
        ]
        return new_urls + urls

    def get_queryset(self, request):
        employee_group_id = request.GET.get('employee_group', None)
        if not employee_group_id:
            employee_group_id = EmployeeGroup.objects.values_list('id', flat=True).first()
        qs = Employee.objects.filter(employee_group_id=employee_group_id).exclude(dismissal_date__lte=self.first_date)
        return qs

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['days'] = []
        extra_context['egf'] = EmployeeWorkTimeHeader(request.GET)
        if extra_context['egf'] and 'date' in extra_context['egf'].data:
            year, month = extra_context['egf'].data['date'].split('-')
            extra_context['year'] = year
            month = month[1] if month[0] == '0' else month
            extra_context['month'] = month
            extra_context['l_day'] = last_day(int(year), int(month))
        else:
            today = datetime.today()
            year = today.year
            month = today.month
            extra_context['date'] = f'{year}-{month}'
            extra_context['egf'].fields['date'].initial = f'{year}-{month}'
            extra_context['year'] = today.year
            extra_context['month'] = today.month
            extra_context['l_day'] = last_day(today.year, today.month)
            extra_context['egf'].fields['date'].initial = f'{year}-{month}'

        for day in range(1, extra_context['l_day'] + 1):
            extra_context['days'].append(date(int(year), int(month), int(day)))
        self.first_date = date(int(year), int(month), 1)
        qs = self.get_queryset(request)
        extra_context['qs'] = qs
        ids = qs.values_list('id', flat=True)
        et = self.TimesModel.objects.filter(employee_id__in=ids, date__gte=self.first_date, date__lte=date(int(year), int(month), extra_context['l_day']))

        employee_times = {}
        for employee in et:
            if employee.employee_id not in employee_times:
                employee_times[employee.employee_id] = {}
            if employee.date not in employee_times[employee.employee_id]:
                employee_times[employee.employee_id][employee.date] = []
            employee_times[employee.employee_id][employee.date].append(employee)
        extra_context['employee_times'] = employee_times
        extra_context['is_hours'] = self.is_hours
        return super().changelist_view(request, extra_context=extra_context)

    class Media:
        js = ('employee/js/work_time.js',)


@admin.register(EmployeeJobTime)
class EmployeeJobTimeAdmin(EmployeeWorkTimeAdmin):
    TimesModel = EmployeeWorkItem
    is_hours = False


@admin.register(EmployeeTime)
class EmployeeTimeAdmin(VektorAdmin):
    list_display = ('employee', 'date', 'project', 'hours', 'ratio', 'type')
    readonly_fields = ['salary_employee', 'created_at', 'created_by', 'updated_at', 'updated_by']
    fieldsets = [
        (None, {'fields': [('employee', 'date', 'project'), ('hours', 'ratio', 'type')]}),
    ]
    popup_response_template = 'admin/core/popup_response.html'
    add_form_template = 'admin/employee/add_form.html'
    autocomplete_fields = ['project', ]


@admin.register(EmployeeWorkItem)
class EmployeeWorkItemAdmin(VektorAdmin):
    fieldsets = (
        (None, {'fields': [('work', 'amount', 'notes')]}),
        (None, {'fields': [('employee', 'date')], 'classes': ['hidden']}),
    )
    # readonly_fields = ['employee', 'created_at', 'created_by', 'updated_at', 'updated_by']
    popup_response_template = 'admin/core/popup_response.html'
    add_form_template = 'admin/employee/add_form.html'
    autocomplete_fields = ['work', ]


class EmployeeCreditPaymentInlineAdmin(admin.TabularInline):
    model = EmployeeCreditPayment
    extra = 0
    fields = ['payment_date', 'payment_amount', 'paid_amount']

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(EmployeeCredit)
class EmployeeCreditAdmin(VektorAdmin):
    list_display = ['employee', 'credit_date', 'credit_amount', 'payments_count']
    autocomplete_fields = ['employee']
    fieldsets = [
        [None, {'fields': ['employee', 'credit_date', 'date_first_payment', 'credit_amount', 'payments_count', 'payment_amount', 'notes']}],
    ]
    inlines = [EmployeeCreditPaymentInlineAdmin]
    form = EmployeeCreditForm
    add_form_template = 'admin/employee/add_credit_form.html'
    save_as_continue = False
    save_as = False

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        date_payment = form.cleaned_data['date_first_payment']
        payment_amount = form.cleaned_data['payment_amount']
        payments_count = form.cleaned_data['payments_count']
        credit_amount = decimal.Decimal(obj.credit_amount)
        if not payment_amount:
            payment_amount = credit_amount // payments_count + 1
        for _ in range(payments_count):
            if credit_amount <= payment_amount:
                payment_amount = credit_amount
            else:
                credit_amount -= payment_amount
            ecp = EmployeeCreditPayment()
            ecp.employee_credit = obj
            ecp.payment_amount = payment_amount
            ecp.payment_date = date_payment
            ecp.save()
            date_payment = add_months(date_payment, 1)

    class Media:
        js = ('employee/js/credit_payment.js',)