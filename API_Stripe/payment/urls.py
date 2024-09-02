from django.urls import path
from . import views 


app_name = 'payment'
urlpatterns = [
    path('', views.index, name='index'),
    path('item/<int:item_id>', views.get_item, name='item_detail'),
    path('buy/<int:item_id>', views.buy_item, name='buy'),
    path('success/', views.success),
    path('cancel/', views.cancel),
]
