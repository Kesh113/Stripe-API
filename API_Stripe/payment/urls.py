from django.urls import path
from . import views 


app_name = 'payment'
urlpatterns = [
    path('', views.index, name='index'),
    path('catalog/', views.catalog, name='catalog'),
    path('item/<int:item_id>', views.get_item, name='item_detail'),
    path('cart/<str:user_name>/delete', views.delete_order, name='delete'),
    path('cart/<str:user_name>', views.cart, name='cart'),
    path('buy/<int:order_id>', views.buy_item, name='buy'),
    path('success/<str:user_name>', views.success, name='success'),
    path('cancel/', views.cancel, name='cancel'),
    
]
