from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display  = ['username', 'email', 'company_name', 'phone', 'is_active', 'date_joined']
    list_filter   = ['is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'company_name']
    ordering      = ['-date_joined']
    fieldsets     = UserAdmin.fieldsets + (
        ('Infos entreprise', {'fields': ('company_name', 'phone', 'currency')}),
    )