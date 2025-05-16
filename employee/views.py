from datetime import datetime, timedelta
from typing import Optional, Any, Dict, Type
from urllib.parse import urlencode

from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.auth import get_permission_codename
from django.db import models, transaction
from django.db.models import QuerySet
from django import forms
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import FormView

from employee.models import Employee, EMPLOYEE_STATUS_ACTIVE, EmployeeTime, EmployeeWorkItem
from django.contrib.admin import helpers


class MassEmployeeWorkTimeView(FormView):
    model_admin: admin.ModelAdmin = None
    model = None
    title = 'Массовое назначения часов'
    short_description = 'Массовое назначения часов'
    template_name = 'admin/employee/mass_add_time.html'
    submit = "Назначить"
    is_hours: bool = True

    queryset: models.QuerySet

    def __init__(self, *,
                 model_admin: admin.ModelAdmin,
                 **kwargs: Any):
        super().__init__(**kwargs)
        self.model_admin = model_admin
        self.is_hours = kwargs.get('is_hours', True)
        if not self.is_hours:
            self.title = 'Массовое назначения работ'
            self.short_description = 'Массовое назначения работ'

    def get_date(self, dt: str) -> str:
        z = dt.split('-')
        if z and len(z) == 2:
            if len(z[1]) == 1:
                dt = f'{z[0]}-0{z[1]}'
        return dt

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        cd = super().get_context_data(**kwargs)
        has_view_permission = self.model_admin.has_view_permission(self.request)
        employee_group = self.request.GET.get('employee_group', 1)
        dt = self.request.GET.get('date', f'{datetime.now().year}-{datetime.now().month}')
        dt = self.get_date(dt)
        cd.update({
            'has_view_permission': has_view_permission,
            'opts': self.model_admin.opts,
            'dt': dt,
            'title': self.title,
            'button': self.submit,
            # 'redirect_form': self.get_redirect_form(),
            'adminform': self.get_admin_form(cd['form'], dt, employee_group),
            'media': self.model_admin.media + cd['form'].media
        })
        return cd

    def get_admin_form(self, form: forms.ModelForm, dt, employee_group) -> helpers.AdminForm:
        form.fields['employee_group'].initial = employee_group or 1
        form.fields['employee_ids'].queryset = Employee.objects.filter(status=EMPLOYEE_STATUS_ACTIVE,
                                                                       employee_group_id=employee_group).order_by('id')
        fieldsets = [(None, {'fields': list(form.fields)})]
        admin_form = helpers.AdminForm(
            form,
            fieldsets,
            prepopulated_fields={},
            model_admin=self.model_admin)
        return admin_form

    def form_valid(self, form):
        date_from = form.cleaned_data['date_from']
        date_to = form.cleaned_data['date_to']
        self.employee_group = form.cleaned_data['employee_group'].pk
        self.date = self.get_date(f"{form.cleaned_data['date_from'].year}-{form.cleaned_data['date_from'].month}")
        dates = [date_from + timedelta(days=x) for x in range(0, 1 + (date_to - date_from).days)]
        with transaction.atomic():
            for employee in form.cleaned_data['employee_ids']:
                for dt in dates:
                    if self.is_hours:
                        ewt = EmployeeTime()
                        ewt.employee = employee
                        ewt.project = form.cleaned_data['project']
                        ewt.date = dt
                        ewt.hours = form.cleaned_data['hours']
                        ewt.ratio = form.cleaned_data['ratio']
                        ewt.type = form.cleaned_data['type']
                        ewt.notes = form.cleaned_data['notes']
                        ewt.save()
                    else:
                        ewt = EmployeeWorkItem()
                        ewt.employee = employee
                        ewt.work = form.cleaned_data['work']
                        ewt.date = dt
                        ewt.amount = form.cleaned_data['amount']
                        ewt.notes = form.cleaned_data['notes']
                        ewt.save()

        return super().form_valid(form)

    def get_success_url(self):
        uri = urlencode({'employee_group': self.employee_group, 'date': self.date})
        url = '/admin/employee/employeeworktime/' if self.is_hours else '/admin/employee/employeejobtime'
        url = url + '?' + uri
        return url
