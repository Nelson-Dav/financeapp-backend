from django.contrib import admin
from .models import Budget, Debt

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['category', 'amount', 'period', 'month', 'year', 'user']
    list_filter  = ['period', 'year']

@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display  = ['contact', 'type', 'amount', 'due_date', 'is_paid', 'user']
    list_filter   = ['type', 'is_paid']
    search_fields = ['contact']