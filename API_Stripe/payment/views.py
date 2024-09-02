from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render
import stripe

from .models import Item

from API_Stripe.settings import STRIPE_PUBLISHABLE_KEY as publish_key,\
    STRIPE_SECRET_KEY as secret_key


stripe.api_key = secret_key

def index(request):
    """Вывод каталога товаров из БД"""
    data = Item.objects.all()
    return render(request, 'payment/index.html', {'data': data})

def get_item(request, item_id: int):
    """Вывод информации о выбранном товаре"""
    try:
        item = Item.objects.get(pk=item_id)
    except Item.DoesNotExist:
        raise Http404(f'Товара с id={item_id} не существует')
    return render(request, 'payment/item.html', {'item': item, 'publish_key': publish_key})

def buy_item(request, item_id: int):
    """Отправка запроса Stripe на получение session_id"""
    print(publish_key)
    try:
        item = Item.objects.get(pk=item_id)
    except Item.DoesNotExist:
        raise Http404(f'Товара с id={item_id} не существует')
    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'], 
        line_items=[{'price_data': {'currency': 'usd', 'product_data': 
            {'name': item.name, 'description': item.description or None}, 
            'unit_amount': int(item.price)}, 'quantity': 1}],
        metadata={
            'product_id': item_id
        },
        mode='payment', 
        success_url='http://127.0.0.1:8000/success/', 
        cancel_url='http://127.0.0.1:8000/cancel/'
    )
    return JsonResponse({'id': checkout_session.id})

def success(request):
    """Ответ при успешной оплате"""
    return HttpResponse('Оплата произошла успешно')

def cancel(request):
    """Ответ при неуспешной оплате"""
    return HttpResponse('Оплата была отменена')