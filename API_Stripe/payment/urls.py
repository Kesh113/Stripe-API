from django.urls import path, include
from . import views 


app_name = 'payment'
urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/signup/', views.SignUpView.as_view(), name='signup'),
    path('currency/', views.currency, name='currency'),
    path('catalog/', views.catalog, name='catalog'),
    path('item/<int:item_id>', views.get_item, name='item_detail'),
    path('cart/delete', views.delete_order, name='delete'),
    path('cart/', views.cart, name='cart'),
    path('buy/', views.buy_item, name='buy'),
    path('success/', views.success, name='success'),
    path('cancel/', views.cancel, name='cancel'),
    path("accounts/", include("django.contrib.auth.urls"))
]
