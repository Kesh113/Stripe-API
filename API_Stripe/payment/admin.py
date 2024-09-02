from django.contrib import admin
from .models import Item

@admin.register(Item)
class AdminItem(admin.ModelAdmin):
    list_display = ['id', 'name', 'price']
    list_display_links = ['name']
    list_per_page = 10
    list_filter = ['name', 'price']

