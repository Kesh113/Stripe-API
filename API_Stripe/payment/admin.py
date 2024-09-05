from django.contrib import admin
from .models import Item, Order, Discount, Tax, OrderItems

@admin.register(Item)
class AdminItem(admin.ModelAdmin):
    list_display = ['id', 'name', 'price', 'currency']
    list_display_links = ['id', 'name',]
    list_per_page = 10
    list_filter = ['name', 'price', 'currency']
    

@admin.register(Order)
class AdminOrder(admin.ModelAdmin):
    fields = ['user', 'discount', 'tax', 'total', 'order_currency']
    list_display = ['id', 'user', 'discount', 'tax', 'total', 'order_currency']
    list_display_links = ['id', 'user']
    list_per_page = 10
    list_filter = ['user', 'total', 'order_currency']
    
@admin.register(Discount)
class AdminDiscount(admin.ModelAdmin):
    list_display = ['id','name', 'discount', 'duration']
    list_display_links = ['id','name']
    
@admin.register(Tax)
class AdminTax(admin.ModelAdmin):
    list_display = ['id', 'name', 'tax', 'inclusive', 'country']
    list_display_links = ['id', 'name']
    
@admin.register(OrderItems)
class AdminOrderItems(admin.ModelAdmin):
    list_display = ['id', 'order', 'item', 'quantity']
    list_display_links = ['id', 'order']