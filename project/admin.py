from django.contrib import admin

from core.admin import VektorAdmin
from project.forms import ProjectForm, WorkForm
from project.models import Project, Work, Partner


class ProjectAdmin(VektorAdmin):
    form = ProjectForm
    list_display = ('title', 'status')
    search_fields = ('title', 'status')


class WorkAdmin(VektorAdmin):
    form = WorkForm
    search_fields = ('project__name', 'title',)
    list_display = ('title', 'project', 'started_at', 'ended_at')
    list_filter = ('project', 'started_at', 'ended_at')
    autocomplete_fields = ['project', ]


class PartnerAdmin(VektorAdmin):
    list_display = ('title', 'description')


admin.site.register(Project, ProjectAdmin)
admin.site.register(Work, WorkAdmin)
admin.site.register(Partner, PartnerAdmin)
