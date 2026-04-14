from django.contrib import admin
from .models import Category, Transaction

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ['name', 'type', 'color', 'user']
    list_filter   = ['type']
    search_fields = ['name']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display  = ['date', 'type', 'amount', 'description', 'category', 'user']
    list_filter   = ['type', 'date']
    search_fields = ['description', 'reference']
    ordering      = ['-date']