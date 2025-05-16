from django.contrib import admin

from company.models import Company
from core.admin import VektorAdmin


class CompanyAdmin(VektorAdmin):
    list_display = ('title', 'inn', 'legal_address', 'basis_title', 'director', 'notes')
    search_fields = ('title', 'inn', 'legal_address', 'basis_title', 'director', 'notes')
    readonly_fields = ('created_at', 'created_by', 'updated_at', 'updated_by')


admin.site.register(Company, CompanyAdmin)
