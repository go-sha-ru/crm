from datetime import datetime

from django import template

from employee.models import Employee

register = template.Library()


@register.simple_tag
def get_hours(employee_times, date, employee_id, is_hours=True):
    if employee_id in employee_times:
        if date in employee_times[employee_id]:
            sum = 0
            for employee in employee_times[employee_id][date]:
                if is_hours:
                    if employee.hours:
                        sum += employee.hours
                else:
                    if employee.amount:
                        sum += employee.amount
            return sum if sum else ''
        return ''
    return ''


@register.simple_tag
def get_time_id(employee_times, date, employee_id, is_hours=True):
    if employee_id in employee_times:
        if date in employee_times[employee_id]:
            return employee_times[employee_id][date][0].id
    return ''


@register.filter
def is_weekend(date):
    return date.weekday() == 6 or date.weekday() == 5


@register.simple_tag()
def get_table(form):
    model = form.model_admin.model
    employee_id = form.form.initial['employee']
    dt = form.form.initial['date']
    dt = datetime.strptime(dt, '%d.%m.%Y')
    times = model.objects.filter(employee_id=employee_id, date=dt)
    return [len(times), times, model.is_hours]
