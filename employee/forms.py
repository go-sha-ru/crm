import os
import re
import shutil
import xml.etree.ElementTree as ET
from datetime import datetime

from django.core.files.uploadedfile import InMemoryUploadedFile
from django import forms
from django.conf import settings
from django.db.models import Q

from account.models import Role
from core.utils import last_day
from employee.models import Salary, SalaryView, EmployeeGroup, SALARY_TYPES, SALARY_TYPE_SALARY_CARD, Employee, \
    SalaryEmployeeItem, SalaryEmployee, EmployeeCredit, EMPLOYEE_STATUS_ACTIVE, EMPLOYEE_TIME_TYPE_WORK, \
    EMPLOYEE_TIME_TYPES
from project.models import Project, Work


class SalaryForm(forms.ModelForm):
    file = forms.FileField(required=False)

    def save(self, commit=False):
        salary = super(SalaryForm, self).save(commit=False)
        salary.year = self.cleaned_data['date_first_day'].year
        salary.month = self.cleaned_data['date_first_day'].month
        salary.save()
        return salary

    class Meta:
        model = Salary
        fields = ('date_first_day', 'date_last_day', 'work_hours', 'notes')


class SalaryViewForm(forms.Form):
    salary_view = forms.ModelChoiceField(queryset=SalaryView.objects.all().order_by('id'), label='Вид',
                                         empty_label=None)


class EmployeeGroupForm(forms.Form):
    employee_group = forms.ModelChoiceField(queryset=EmployeeGroup.objects.all().order_by('id'), label='Отдел',
                                            empty_label="Все сотрудники")


class EmployeeWorkTimeHeader(forms.Form):
    date = forms.CharField(label='Месяц', required=False, widget=forms.TextInput(attrs={'type': 'month'}))
    employee_group = forms.ModelChoiceField(queryset=EmployeeGroup.objects.all().order_by('id'), label='Отдел',
                                            required=False,
                                            empty_label=None)


class EmployeeWorkMassTime(forms.Form):
    date_from = forms.DateField(label='Дата с', widget=forms.SelectDateWidget(),
                                initial=datetime(datetime.today().year, datetime.today().month, 1))
    date_to = forms.DateField(label='Дата по', widget=forms.SelectDateWidget(),
                              initial=datetime(datetime.today().year, datetime.today().month, last_day(datetime.today().year, datetime.today().month)))
    employee_group = forms.ModelChoiceField(queryset=EmployeeGroup.objects.all().order_by('id'), label='Отдел',
                                            required=False,
                                            empty_label=None)
    project = forms.ModelChoiceField(queryset=Project.objects.all(), label='Проект', empty_label=None)
    hours = forms.IntegerField(label='Часы', required=True, initial=8)
    ratio = forms.IntegerField(label='Коэффициент', required=True, initial=1)
    type = forms.ChoiceField(label='Тип', required=True, choices=EMPLOYEE_TIME_TYPES,
                             initial=EMPLOYEE_TIME_TYPE_WORK)
    notes = forms.CharField(label='Примечание', required=False, widget=forms.Textarea(attrs={'cols': 80, 'rows': 4}))
    employee_ids = forms.ModelMultipleChoiceField(
        label='Сотрудники',
        queryset=Employee.objects.all().order_by('id'),
        widget=forms.CheckboxSelectMultiple(), )


class EmployeeWorkMassWorkForm(forms.Form):
    date_from = forms.DateField(label='Дата с', widget=forms.SelectDateWidget(),
                                initial=datetime(datetime.today().year, datetime.today().month, 1))
    date_to = forms.DateField(label='Дата по', widget=forms.SelectDateWidget(),
                              initial=datetime(datetime.today().year, datetime.today().month, last_day(datetime.today().year, datetime.today().month)))
    employee_group = forms.ModelChoiceField(queryset=EmployeeGroup.objects.all().order_by('id'), label='Отдел',
                                            required=False,
                                            empty_label=None)
    work = forms.ModelChoiceField(queryset=Work.objects.all(), label='Работа', empty_label=None)
    amount = forms.FloatField(label='Сумма', required=True)
    notes = forms.CharField(label='Примечание', required=False, widget=forms.Textarea(attrs={'cols': 80, 'rows': 4}))
    employee_ids = forms.ModelMultipleChoiceField(
        label='Сотрудники',
        queryset=Employee.objects.all().order_by('id'),
        widget=forms.CheckboxSelectMultiple(), )


class SalaryUploadForm(forms.Form):
    file = forms.FileField(label='Выберите файл')
    type = forms.ChoiceField(label='Тип начисления', choices=SALARY_TYPES, initial=SALARY_TYPE_SALARY_CARD)

    def upload_salary(self, salary):
        salary = salary
        f = self.cleaned_data['file']
        items = {}
        extracted = False
        errors = {}
        success = {}
        try:
            f_name = f'{settings.TMP_DIR}{f.name}'
            if os.path.isdir(f_name + "_files"):
                shutil.rmtree(f_name + "_files")
            else:
                os.mkdir(f_name + "_files")
            if f.name.endswith == 'zip':
                import zipfile
                zip_file = zipfile.ZipFile(f.file)
                for name in zip_file.namelist():
                    zip_file.extract(name, f.name + "_files/")
                zip_file.close()
            elif f.name.endswith('.7z'):
                import py7zr
                with py7zr.SevenZipFile(f.file, 'r') as archive:
                    archive.extractall(path=f_name + "_files")
            elif f.name.endswith('.xml'):
                with open(f_name + "_files/" + f.name, 'w') as xml_file:
                    xml_file.write(f.file.read())
            elif f.name.endswith('.txt'):
                with open(f_name + "_files/" + f.name, 'w') as txt_file:
                    txt_file.write(f.file.read())
            else:
                raise Exception('Is no archive file')

            allfiles = [os.path.join(dirpath, f) for (dirpath, dirnames, filenames) in os.walk(f_name + "_files") for f
                        in filenames]
            for filename in allfiles:
                errors[filename] = []
                data, number, file_items = self.load_file_to_list(filename)
                if len(file_items):
                    if not data:
                        errors[filename].append('Не найдена дата реестра')
                    for item in file_items:
                        employee = Employee.objects.filter(bank_account_number=item["bank_account_number"],
                                                           employment_date__lte=salary.date_last_day).filter(
                            Q(dismissal_date__isnull=True) | Q(dismissal_date__gte=salary.date_first_day)).first()
                        if employee:
                            salary_employee = salary.get_salary_employee_by_employee(employee_id=employee.id)
                            item['model'] = salary_employee
                            notes = f'Реестр {number} от {data.strftime("%d.%m.%Y")}'
                            exist = SalaryEmployeeItem.objects.filter(salary_employee_id=salary_employee.pk, date=data,
                                                                      notes=notes).exists()
                            if exist:
                                errors[filename].append(f'{notes} для {employee.__str__()}  был загружен ранее')
                        else:
                            errors[filename].append(f'Не найден работник со счетом: {item["bank_account_number"]}')

                else:
                    errors[filename].append('Не удалось загрузить файл')
                if not len(errors[filename]):
                    for item in file_items:
                        if not item['model'].pk:
                            item['model'].salary_id = salary.pk
                            item['model'].save()
                        sei = SalaryEmployeeItem()
                        sei.salary_employee_id = item['model'].pk
                        sei.type = self.cleaned_data['type']
                        sei.date = item['date']
                        sei.viewable_amount = item['amount']
                        sei.notes = f'Реестр {number} от {data.strftime("%d.%m.%Y")}'
                        sei.save()
                    success[filename] = True
            return success, errors
        except Exception as e:
            errors['catch'] = type(e)
            errors['exception'] = e
        return success, errors

    def load_file_to_list(self, filename):
        data, number = None, None
        items = []
        if filename.endswith('txt'):
            pass
            with open(filename, encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines:
                    if match := re.search(r'№\s+(\d+)\s+от\s+(\d+\.\d+\.\d+)\s+г\.', line):
                        number = match.group(1)
                        data = match.group(2)
                        data = datetime.strptime(data, '%d.%m.%Y')
                    row = line.split('\t')
                    if row[0] == '№ п/п':
                        numbers = {}
                        for idx, item in enumerate(row):
                            if item == 'Лицевой счет':
                                numbers['bank_account_number'] = idx
                            if item == 'Фамилия, имя, отчество':
                                numbers['fio'] = idx
                            if item == 'Сумма':
                                numbers['amount'] = idx
                        if len(numbers) != 3:
                            numbers = None
                        continue
                    if numbers:
                        if row[numbers['bank_account_number']] == '2':
                            continue
                        if row[numbers['bank_account_number']] == '':
                            break
                        amount = row[numbers['amount']].replace(',', '.')
                        re.sub(r'/[^\d\.]/', '', amount)
                        amount = float(amount)
                        items.append({'amount': amount,
                                      'bank_account_number': row[numbers['bank_account_number']],
                                      'date': data})
        elif filename.endswith('xml'):
            tree = ET.parse(filename)
            root = tree.getroot()
            attributes = root.attrib
            number = attributes['НомерРеестра']
            data = attributes['ДатаРеестра']
            data = datetime.strptime(data, '%Y-%m-%d')
            employees = root.findall('ЗачислениеЗарплаты/Сотрудник')
            for employee in employees:
                amount = employee.find('Сумма').text
                bank_account_number = employee.find('').text
                items.append({'amount': amount, 'bank_account_number': bank_account_number, 'date': data})
        return data, number, items


class SalaryEmployeeItemForm(forms.ModelForm):
    salary_id = forms.IntegerField(widget=forms.HiddenInput())
    employee_id = forms.IntegerField(widget=forms.HiddenInput())
    salary_employee_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = SalaryEmployeeItem
        fields = ['type', 'date', 'amount', 'notes']


class EmployeeCreditForm(forms.ModelForm):
    payment_amount = forms.DecimalField(required=False, label='Или размер платежа')
    date_first_payment = forms.DateField(required=True, label='Дата первого платежа',
                                         widget=forms.TextInput(attrs={'class': 'vDateField'}))
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': '3'}), required=False, label='Примечание')

    class Meta:
        model = EmployeeCredit
        fields = ['employee', 'credit_date', 'credit_amount', 'payments_count', 'notes']
