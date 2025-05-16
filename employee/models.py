from datetime import datetime
from math import ceil
from operator import attrgetter
from typing import Type

from django.conf import settings
from django.db import models
from django.db.models import Q, Count
from django.urls import reverse
from django.utils.safestring import mark_safe

from account.models import Role
from company.models import Company
from core.models import DateUserMixin
from core.utils import add_months, last_day
from project.models import Project, Work

EMPLOYEE_STATUS_ACTIVE = 'active'
EMPLOYEE_STATUS_FIRED = 'fired'
EMPLOYEE_STATUSES = (
    ('active', 'Активный'),
    ('fired', 'Уволенный'),
)

EMPLOYEE_TIME_TYPE_WORK = 'work'
EMPLOYEE_TIME_TYPE_LEAVE = 'leave'
EMPLOYEE_TIME_TYPE_VACATION = 'vacation'
EMPLOYEE_TIME_TYPE_SICK = 'sick'

EMPLOYEE_TIME_TYPES = (
    (EMPLOYEE_TIME_TYPE_WORK, 'Рабочее время'),
    (EMPLOYEE_TIME_TYPE_LEAVE, 'Административный отпуск'),
    (EMPLOYEE_TIME_TYPE_VACATION, 'Отпуск'),
    (EMPLOYEE_TIME_TYPE_SICK, 'Больничный'),
)

REMUNERATION_TYPE_SALARY = 'salary'
REMUNERATION_TYPE_HOURLY = 'hourly'
REMUNERATION_TYPES = (
    (REMUNERATION_TYPE_SALARY, 'Оклад'),
    (REMUNERATION_TYPE_HOURLY, 'Почасовая'),
)

SALARY_TYPE_PREVIOUS = 'prev'
SALARY_TYPE_HOURS = 'hours'
SALARY_TYPE_VACATION = 'vacation'
SALARY_TYPE_SICK = 'sick'
SALARY_TYPE_WORK = 'work'
SALARY_TYPE_FUEL = 'fuel'
SALARY_TYPE_TRIP = 'trip'
SALARY_TYPE_LOAN = 'loan'
SALARY_TYPE_BONUS = 'bonus'
SALARY_TYPE_DISMISSAL = 'dismissal'
SALARY_TYPE_OTHER = 'other'
SALARY_TYPE_ADVANCE = 'advance'
SALARY_TYPE_SALARY = 'salary'
SALARY_TYPE_ADVANCE_CARD = 'advance_card'
SALARY_TYPE_SALARY_CARD = 'salary_card'
SALARY_TYPE_CASH = 'cash'
SALARY_TYPE_LOAN_RETURN = 'loan_return'
SALARY_TYPE_FINE = 'fine'

SALARY_TYPES = (
    (SALARY_TYPE_ADVANCE, 'Аванс'),
    (SALARY_TYPE_SALARY, 'Зарплата'),
    (SALARY_TYPE_ADVANCE_CARD, 'Аванс на карту'),
    (SALARY_TYPE_SALARY_CARD, 'Зарплата на карту'),
    (SALARY_TYPE_CASH, 'Выдача наличных'),
    (SALARY_TYPE_LOAN_RETURN, 'Возврат кредита'),
    (SALARY_TYPE_FINE, 'Штраф'),
    (SALARY_TYPE_PREVIOUS, 'Перенос'),
    (SALARY_TYPE_HOURS, 'Начисления'),
    (SALARY_TYPE_VACATION, 'Отпускные'),
    (SALARY_TYPE_SICK, 'Больничные'),
    (SALARY_TYPE_WORK, 'Работы'),
    (SALARY_TYPE_FUEL, 'ГСМ'),
    (SALARY_TYPE_TRIP, 'Командировочные'),
    (SALARY_TYPE_LOAN, 'Зачисление кредита'),
    (SALARY_TYPE_BONUS, 'Премия'),
    (SALARY_TYPE_DISMISSAL, 'Расчет при увольнении'),
    (SALARY_TYPE_OTHER, 'Другое'),
)


class EmployeeManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def get_active(self):
        return self.get_queryset().filter(status=EMPLOYEE_STATUS_ACTIVE)


class Employee(DateUserMixin):
    role = models.ForeignKey(Role, on_delete=models.PROTECT, verbose_name="Должность")
    role_note = models.CharField(max_length=255, blank=True, verbose_name="Примечания к должности")
    employee_group = models.ForeignKey("EmployeeGroup", on_delete=models.PROTECT, verbose_name="Отдел")
    surname = models.CharField(max_length=255, blank=True, verbose_name="Фамилия")
    firstname = models.CharField(max_length=255, blank=True, verbose_name="Имя")
    patronymic = models.CharField(max_length=255, blank=True, verbose_name="Отчество")
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE,
                                null=True, blank=True,
                                related_name='employee',
                                verbose_name="Пользователь")
    employment_date = models.DateField(verbose_name="Дата принятия на работу")
    dismissal_date = models.DateField(verbose_name="Дата увольнения", blank=True, null=True)
    remuneration_to_delete = models.CharField(max_length=64, choices=REMUNERATION_TYPES,
                                              default=REMUNERATION_TYPE_SALARY, verbose_name='Вид оплаты труда')
    salary_rate_to_delete = models.FloatField(verbose_name='Ставка')
    status = models.CharField(max_length=16, verbose_name="Статус", choices=EMPLOYEE_STATUSES,
                              default=EMPLOYEE_STATUS_ACTIVE)
    bank_account_number = models.CharField(max_length=255, blank=True, verbose_name='Номер счета')
    bank_bik = models.CharField(max_length=255, blank=True, verbose_name='БИК банка')
    company = models.ForeignKey(Company, verbose_name="Компания", on_delete=models.PROTECT, blank=True, null=True)
    salary = models.ManyToManyField('Salary', through='SalaryEmployee')

    objects = EmployeeManager()

    def __str__(self):
        return f"{self.surname} {self.firstname} {self.patronymic}"

    def fio(self):
        s = f"{self.surname}"
        if self.firstname:
            s += f'&nbsp;{self.firstname[0].upper()}.'
        if self.patronymic:
            s += f'&nbsp;{self.patronymic[0].upper()}.'
        return mark_safe(s)

    def get_times(self, dt):
        dt = datetime.strptime(dt, '%d.%m.%Y')
        times = self.employee_time.filter(date=dt)
        return times

    def get_job_times(self, dt):
        dt = datetime.strptime(dt, '%d.%m.%Y')
        times = self.employeeworkitem_set.filter(date=dt)
        return times

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        ordering = ['surname']
        db_table = 'employee'


class EmployeeTransfer(DateUserMixin):
    employee = models.ForeignKey(Employee, verbose_name='Сотрудник', on_delete=models.PROTECT,)
    date_from = models.DateField(verbose_name='Дата перевода')
    employee_group_from = models.ForeignKey("EmployeeGroup", on_delete=models.PROTECT, verbose_name="Из какого отдела", related_name='employee_group_from', null=True, blank=True)
    employee_group_to = models.ForeignKey("EmployeeGroup", on_delete=models.PROTECT, verbose_name="В какой отдел", related_name='employee_group_to')

    def fio(self):
        return self.employee.fio()

    def employee_group(self):
        return self.employee.employee_group

    def __str__(self):
        return f"{self.employee.fio(), self.date_from} {self.employee_group_from} {self.employee_group_to}"

    class Meta:
        verbose_name = "Смена отдела сотрудника"
        verbose_name_plural = "смена отдела сотрудника"
        ordering = ['employee__surname']
        db_table = 'employee_transfer'


class EmployeeWorkTime(Employee):

    class Meta:
        proxy = True
        verbose_name = 'Учет времени'
        verbose_name_plural = 'Учет времени'


class EmployeeJobTime(Employee):

    class Meta:
        proxy = True
        verbose_name = 'Учет работ'
        verbose_name_plural = 'Учет работ'


class EmployeeSalary(DateUserMixin):
    employee = models.ForeignKey(Employee, verbose_name='Сотрудник', on_delete=models.PROTECT, )
    from_date = models.DateField(verbose_name='Дата начала', null=True, blank=True)
    to_date = models.DateField(verbose_name='Дата завершения', null=True, blank=True)
    salary_rate = models.FloatField(verbose_name='Ставка', null=True, blank=True)
    remuneration_type = models.CharField(max_length=64, choices=REMUNERATION_TYPES, default=REMUNERATION_TYPE_SALARY,
                                         verbose_name='Тип')

    def __str__(self):
        return f"{self.employee}: ({self.from_date} {self.to_date}) {self.salary_rate:.2f} {self.get_remuneration_type_display()}"

    class Meta:
        db_table = 'employee_salary'


class EmployeeGroup(DateUserMixin):
    title = models.CharField(max_length=255, verbose_name='Название')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Отдел"
        verbose_name_plural = "Отделы"
        ordering = ['id']
        db_table = 'employee_group'


class Salary(DateUserMixin):
    year = models.PositiveSmallIntegerField(verbose_name='Год')
    month = models.PositiveSmallIntegerField(verbose_name='Месяц')
    date_first_day = models.DateField(verbose_name='Дата первого дня')
    date_last_day = models.DateField(verbose_name='Дата последнего дня')
    work_hours = models.PositiveSmallIntegerField(verbose_name='Рабочих часов')
    notes = models.TextField(verbose_name='Заметки', blank=True, default='', db_column='notes')
    employees = models.ManyToManyField(Employee, through='SalaryEmployee', related_name='salary_employees')

    def __str__(self):
        return f'{self.get_name()}: {self.work_hours} часов'

    def get_name(self):
        import calendar
        import locale
        locale.setlocale(locale.LC_TIME, 'ru_RU')
        month = calendar.month_name[self.month]
        return f'Зарплата {month} {self.year}'

    def move_next(self):
        date_first_day = self.date_first_day
        add_months(date_first_day, 1)
        params = {'year': datetime.today().year, 'month': datetime.today().month}
        next_salary = Salary.objects.filter(**params)
        if not next_salary:
            next_salary = Salary(**params)
            next_salary.fill_dates()
        for salary_employee in self.get_salary_employees():
            if salary_employee.employee.dismissal_date and salary_employee.employee.dismissal_date < date_first_day:
                continue
            salary_employee.set_total_amount()
            total = salary_employee.amount_all
            next_salary_employee = next_salary.get_salary_employee_by_employee(salary_employee.employee_id)
            next_salary_employee.set_total_amount()
            next_total = next_salary_employee.amount_all
            if total != next_total:
                amount = total - next_total
                if not next_salary.pk:
                    next_salary.save()
                if not next_salary_employee.pk:
                    next_salary_employee.salary_id = next_salary.pk
                    next_salary_employee.save()
                sei = SalaryEmployeeItem()
                sei.salary_employee_id = next_salary_employee.pk
                sei.date = datetime.today()
                sei.amount = amount
                sei.notes = f'Перенос за вычетом ранее перенесенной суммы {next_total}' if next_total else ''
                sei.save()

    def fill_dates(self):
        self.date_first_day = datetime(self.year, self.month, 1)
        self.date_last_day = datetime(self.year, self.month, last_day(self.year, self.month))

    def get_salary_employees(self):
        salary_employees = []
        employee_ids = []
        if self.pk:
            salary_employees = self.salaryemployee_set.select_related('employee').all()
            employee_ids = set(salary_employees.values_list('employee_id', flat=True))
        employees = Employee.objects.filter(employment_date__lte=self.date_last_day).filter(
            Q(dismissal_date__gte=self.date_first_day) | Q(dismissal_date__isnull=True)).exclude(id__in=employee_ids)
        salary_employees = list(salary_employees)
        for employee in employees:
            salary_employees.append(SalaryEmployee(salary_id=self.pk, employee=employee))

        sorted(salary_employees, key=attrgetter('employee.employee_group_id', 'employee.surname', 'employee.firstname'))
        return salary_employees

    def get_salary_employee_by_employee(self, employee_id: Type[int]):
        salary_employees = self.get_salary_employees()
        for salary_employee in salary_employees:
            if salary_employee.employee_id == employee_id:
                if not salary_employee.pk:
                    salary_employee.salary_id = self.pk
                    salary_employee.save()
                return salary_employee
        return None

    def calculate_salary(self):
        if not self.work_hours:
            return False
        salary_employees = self.get_salary_employees()
        for salary_employee in salary_employees:
            times = EmployeeTime.objects.filter(employee_id=salary_employee.employee_id, date__gte=self.date_first_day,
                                                date__lte=self.date_last_day)
            if not times:
                continue
            if not salary_employee.pk:
                salary_employee.save()
            rates = salary_employee.salary_employee_rate.all()
            if not rates.count():
                salary_employee.fill_rates()
                rates = salary_employee.salary_employee_rate.all()
            if not rates.count():
                continue
            uncalculated_total_time = {}
            total_time = {}
            for rate in rates:
                uncalculated_total_time[rate.pk] = 0
                total_time[rate.pk] = 0
            for time in times:
                if time.type == EMPLOYEE_TIME_TYPE_WORK:
                    for rate in rates:
                        if rate.from_date > time.date or rate.to_date < time.date:
                            continue
                        total_time[rate.pk] += time.hours * time.ratio
                        if not time.salary_employee_id:
                            uncalculated_total_time[rate.pk] += time.hours * time.ratio
                        break
            for rate in rates:
                if total_time[rate.pk]:
                    total_time[rate.pk] = round(total_time[rate.pk], 2)
                    rate.hours = total_time[rate.pk]
                    rate.save(update_fields=['hours'])
                if uncalculated_total_time[rate.pk]:
                    total_time[rate.pk] = round(uncalculated_total_time[rate.pk], 2)
                    sei = SalaryEmployeeItem(salary_employee_id=salary_employee.pk, date=self.date_last_day)
                    sei.type = SALARY_TYPE_HOURS
                    if rate.remuneration_type == REMUNERATION_TYPE_HOURLY:
                        sei.amount = rate.salary_rate * uncalculated_total_time[rate.pk]
                    else:
                        sei.amount = ceil(
                            rate.salary_rate * (uncalculated_total_time[rate.pk] / self.work_hours) * 100) / 100
                    sei.save()
            for time in times:
                if time.type == EMPLOYEE_TIME_TYPE_WORK:
                    if not time.salary_employee_id:
                        time.salary_employee_id = salary_employee.pk
                        time.save(update_fields=['salary_employee_id'])
            works = EmployeeWorkItem.objects.filter(employee_id=salary_employee.employee_id,
                                                    date__gte=self.date_first_day, date__lte=self.date_last_day)
            for work in works:
                if not work.salary_employee_item_id:
                    if not salary_employee.pk:
                        salary_employee.salary_id = self.pk
                        salary_employee.save(update_fields=['salary_id'])
                    sei = SalaryEmployeeItem(salary_employee_id=salary_employee.pk, date=work.date)
                    sei.type = SALARY_TYPE_WORK
                    sei.amount = work.amount
                    try:
                        sei.save()
                        work.salary_employee_item_id = sei.pk
                        work.save(update_fields=['salary_employee_item_id'])
                    except Exception as e:
                        print(e)

            credits = EmployeeCreditPayment.objects.filter(employee_credit__employee_id=salary_employee.employee_id,
                                                           payment_date__gte=self.date_first_day,
                                                           payment_date__lte=self.date_last_day,
                                                           employee_credit__salary_employee_item_id__isnull=True)
            for credit in credits:
                amount = credit.payment_amount - credit.paid_amount
                if not salary_employee.pk:
                    salary_employee.salary_id = self.pk
                    salary_employee.save(update_fields=['salary_id'])
                sei = SalaryEmployeeItem(salary_employee_id=salary_employee.pk, date=credit.payment_date)
                sei.type = SALARY_TYPE_LOAN_RETURN
                sei.amount = -amount
                try:
                    sei.save()
                    credit.salary_employee_item_id = sei.pk
                    credit.paid_amount = credit.payment_amount
                    credit.save(update_fields=['paid_amount', 'salary_employee_item_id'])

                except Exception as e:
                    print(e)
        return True

    class Meta:
        db_table = 'salary'
        verbose_name = 'Зарплата'
        verbose_name_plural = 'Зарплата'


class SalaryEmployee(DateUserMixin):
    salary = models.ForeignKey(Salary, on_delete=models.CASCADE, verbose_name='Зарплата')
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='Сотрудник')
    salary_rate_to_delete = models.FloatField(verbose_name='Ставка', blank=True, null=True)
    hours_to_delete = models.FloatField(verbose_name='', blank=True, null=True)

    def fill_rates(self):
        rates = SalaryEmployeeRate.objects.filter(salary_employee__employee_id=self.employee_id).filter(
            Q(from_date__isnull=True) | Q(from_date__lte=self.salary.date_last_day)).filter(
            Q(to_date__isnull=True) | Q(to_date__gte=self.salary.date_first_day))
        for rate in rates:
            from_date = rate.from_date if rate.from_date else self.salary.date_first_day
            if from_date < self.salary.date_first_day:
                from_date = self.salary.date_first_day
            to_date = rate.to_date if rate.to_date else self.salary.date_last_day
            if to_date > self.salary.date_last_day:
                to_date = self.salary.date_last_day
            SalaryEmployeeRate.objects.create(salary_employee_id=self.pk, from_date=from_date, to_date=to_date,
                                              salary_rate=rate.salary_rate, remuneration_type=rate.remuneration_type)

    def set_total_amount_by_group(self, salary_view_id):
        self.total_amount = {}
        group_types = {}
        prev_stgi = None
        for stgi in SalaryTypeGroupItem.objects.filter(salary_type_group__salary_view_id=salary_view_id).order_by(
                'salary_type_group__title'):
            if not prev_stgi or prev_stgi.salary_type_group_id != stgi.salary_type_group_id:
                group_types[stgi.salary_type_group_id] = []
                prev_stgi = stgi
            group_types[stgi.salary_type_group_id].append(stgi.type)

        for k, v in group_types.items():
            amounts = SalaryEmployeeItem.objects.filter(salary_employee_id=self.pk, type__in=v)
            total = 0
            for amount in amounts:
                total += amount.amount
            self.total_amount[k] = total if total != 0 else None

    def set_total_amount(self):
        self.amount_all = 0
        amounts = SalaryEmployeeItem.objects.filter(salary_employee_id=self.pk)
        total = 0
        for amount in amounts:
            total += amount.amount
        self.amount_all += total

    def get_items_by_group(self, group_id=None):
        grouped_types = SalaryTypeGroupItem.objects.values_list('type', flat=True)
        if group_id is None:
            grouped_types = grouped_types.annotate(dcount=Count('type'))
        else:
            grouped_types = grouped_types.filter(salary_type_group_id=group_id).annotate(dcount=Count('type'))

    def __str__(self):
        return f"{self.salary} | {self.employee} - {self.salary_rate_to_delete} / {self.hours_to_delete}"

    def get_admin_url_add(self):
        return reverse('admin:employee_salaryemployeeitem_add')

    def get_admin_url_change(self):
        return reverse('admin:employee_salaryemployeeitem_change')

    class Meta:
        db_table = 'salary_employee'


class SalaryEmployeeItem(DateUserMixin):
    salary_employee = models.ForeignKey(SalaryEmployee, on_delete=models.CASCADE, verbose_name='')
    date = models.DateField(verbose_name='Дата')
    amount = models.FloatField(verbose_name='Сумма')
    type = models.CharField(max_length=16, verbose_name='Тип', choices=SALARY_TYPES, default=SALARY_TYPE_SALARY_CARD)
    type_note = models.CharField(max_length=255, verbose_name='Уточнение типа', blank=True, default='')
    notes = models.TextField(verbose_name='Примечание', blank=True, default='')

    def __str__(self):
        return f"{self.salary_employee} | {self.date} | {self.amount} / {self.type}"

    @classmethod
    def reduce_types(cls):
        return [
            SALARY_TYPE_ADVANCE,
            SALARY_TYPE_SALARY,
            SALARY_TYPE_ADVANCE_CARD,
            SALARY_TYPE_SALARY_CARD,
            SALARY_TYPE_CASH,
            SALARY_TYPE_LOAN_RETURN,
            SALARY_TYPE_FINE,
        ]

    @classmethod
    def raise_types(cls):
        return [
            SALARY_TYPE_PREVIOUS,
            SALARY_TYPE_HOURS,
            SALARY_TYPE_VACATION,
            SALARY_TYPE_SICK,
            SALARY_TYPE_WORK,
            SALARY_TYPE_FUEL,
            SALARY_TYPE_TRIP,
            SALARY_TYPE_LOAN,
            SALARY_TYPE_BONUS,
            SALARY_TYPE_DISMISSAL,
            SALARY_TYPE_OTHER,
        ]

    @property
    def viewable_amount(self):
        ret = self.amount * -1 if self.is_reduce() else self.amount
        return ret

    @viewable_amount.setter
    def viewable_amount(self, value):
        self.amount = value * -1 if self.is_reduce() else value
        return

    def is_reduce(self):
        return self.type in self.reduce_types()

    class Meta:
        db_table = 'salary_employee_item'
        verbose_name = 'Начисления/Списания'
        verbose_name_plural = 'Начисления/Списания'


class SalaryEmployeeRate(DateUserMixin):
    salary_employee = models.ForeignKey(SalaryEmployee, on_delete=models.CASCADE, verbose_name='',
                                        related_name='salary_employee_rate')
    from_date = models.DateField(verbose_name='Дата начала')
    to_date = models.DateField(verbose_name='Дата окончания')
    hours = models.FloatField(verbose_name='Сумма')
    salary_rate = models.FloatField(verbose_name='Ставка')
    remuneration_type = models.CharField(max_length=16, verbose_name='Тип', choices=REMUNERATION_TYPES,
                                         default=REMUNERATION_TYPE_SALARY)

    def __str__(self):
        return f"{self.salary_employee} | {self.from_date} - {self.to_date} / {self.hours}"

    class Meta:
        db_table = 'salary_employee_rate'


class SalaryTypeGroup(DateUserMixin):
    title = models.CharField(max_length=255, verbose_name='')
    salary_view = models.ForeignKey('SalaryView', on_delete=models.CASCADE, verbose_name='Вид', null=True, blank=True)

    def __str__(self):
        return self.title

    def get_items_labels(self):
        s_t = {}
        ret = set()
        for item in SALARY_TYPES:
            s_t[item[0]] = item[1]
        stgi = self.salarytypegroupitem_set.all()
        for item in stgi:
            if item.type in s_t:
                ret.add((item.type, s_t[item.type]))
        return tuple(ret)

    class Meta:
        db_table = 'salary_type_group'


class SalaryTypeGroupItem(DateUserMixin):
    salary_type_group = models.ForeignKey(SalaryTypeGroup, on_delete=models.CASCADE, verbose_name='')
    type = models.CharField(max_length=16, verbose_name='Тип', choices=SALARY_TYPES, default=SALARY_TYPE_SALARY_CARD)

    def __str__(self):
        return f'{self.salary_type_group} | {self.type}'

    class Meta:
        db_table = 'salary_type_group_item'


class SalaryView(models.Model):
    title = models.CharField(max_length=255, verbose_name='Название')
    show_time_column = models.BooleanField(verbose_name='Показывать колонку с окладами/временем')
    show_total_column = models.BooleanField(verbose_name='Показывать колонку Итого')

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'salary_view'
        verbose_name = 'Вид отображения таблицы зарплат'
        verbose_name_plural = 'Виды отображения таблицы зарплат'


class EmployeeCredit(DateUserMixin):
    employee = models.ForeignKey(Employee, verbose_name='Сотрудник', on_delete=models.PROTECT, )
    salary_employee_item = models.ForeignKey(SalaryEmployeeItem, on_delete=models.PROTECT, null=True, blank=True)
    credit_amount = models.FloatField(verbose_name='Сумма кредита')
    credit_date = models.DateField(verbose_name='Дата выдачи')
    percent = models.FloatField(verbose_name='Процент', default=0)
    payments_count = models.IntegerField(verbose_name='Количество платежей')
    notes = models.TextField(verbose_name='Примечание', blank=True, null=True)

    def __str__(self):
        return f"{self.employee}: {self.credit_amount} | {self.payments_count}"

    class Meta:
        db_table = 'employee_credit'
        verbose_name = 'Кредит'
        verbose_name_plural = 'Кредиты'


class EmployeeCreditPayment(DateUserMixin):
    employee_credit = models.ForeignKey(EmployeeCredit, verbose_name='Кредит', on_delete=models.PROTECT, )
    salary_employee_item = models.ForeignKey(SalaryEmployeeItem, on_delete=models.PROTECT, null=True, blank=True)
    payment_amount = models.FloatField(verbose_name='Сумма платежа')
    paid_amount = models.FloatField(verbose_name='Оплачено')
    payment_date = models.DateField(verbose_name='Дата платежа')

    def __str__(self):
        return f"{self.employee_credit}: {self.payment_amount} оплачено {self.paid_amount} | {self.payment_date}"

    class Meta:
        db_table = 'employee_credit_payment'
        verbose_name = "Платёж по кредиту"
        verbose_name_plural = "Платежи по кредитам"


class EmployeeTime(DateUserMixin):
    employee = models.ForeignKey(Employee, verbose_name='Сотрудник', on_delete=models.PROTECT, related_name='employee_time')
    project = models.ForeignKey(Project, on_delete=models.PROTECT, verbose_name='Проект')
    date = models.DateField(verbose_name='Дата')
    hours = models.FloatField(verbose_name='Время')
    ratio = models.FloatField(verbose_name='Коэффициент', default=1)
    type = models.CharField(max_length=16, verbose_name='Тип', choices=EMPLOYEE_TIME_TYPES,
                            default=EMPLOYEE_TIME_TYPE_WORK)
    notes = models.TextField(verbose_name='Примечание', blank=True, null=True)
    salary_employee = models.ForeignKey(SalaryEmployee, on_delete=models.CASCADE, verbose_name='')

    @classmethod
    def is_hours(cls):
        return True

    def delete_link(self):
        info = self._meta.app_label, self._meta.model_name
        return reverse('admin:%s_%s_delete' % info, args=(self.pk,))

    class Meta:
        db_table = 'employee_time'
        verbose_name = 'Учёт рабочего времени'
        verbose_name_plural = 'Учёт рабочего времени'


class EmployeeWorkItem(DateUserMixin):
    employee = models.ForeignKey(Employee, verbose_name='Сотрудник', on_delete=models.PROTECT, )
    work = models.ForeignKey(Work, on_delete=models.PROTECT, verbose_name='Работа')
    date = models.DateField(verbose_name='Дата')
    amount = models.FloatField(verbose_name='Сумма')
    notes = models.TextField(verbose_name='Примечание', blank=True, null=True)
    salary_employee_item = models.ForeignKey(SalaryEmployeeItem, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return f"{self.employee} - {self.work} | {self.date} | {self.amount}"

    @classmethod
    def is_hours(cls):
        return False

    def delete_link(self):
        info = self._meta.app_label, self._meta.model_name
        return reverse('admin:%s_%s_delete' % info, args=(self.pk,))

    class Meta:
        db_table = 'employee_work_item'
        verbose_name = 'Сдельная работа'
        verbose_name_plural = 'Сдельные работы'
