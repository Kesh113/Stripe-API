from decimal import Decimal
from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render
from google_currency import convert 
import stripe

from .models import Item, Order

from API_Stripe.settings import STRIPE_PUBLISHABLE_KEY as publish_key,\
    STRIPE_SECRET_KEY as secret_key


stripe.api_key = secret_key
user='Артем'

def has_coupon(discount):
    if discount:
        for coupon in stripe.Coupon.list()['data']:
            if discount.name == coupon['id']:
                break
        else:
            stripe.Coupon.create(
                duration=discount.duration,
                id=discount.name,
                percent_off=discount.discount,
            )
        
def create_session(line_items, order, discount):
    if discount:
        discounts = [{'coupon': discount.name}]
    else:
        discounts = []
    checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'], 
            line_items=line_items,
            metadata={
                'product_id': order.id
            },
            mode='payment',
            discounts=discounts,
            # tax_ids=stripe.Customer.list_tax_ids("cus_NZKoSNZZ58qtO0",),
            success_url='http://127.0.0.1:8000/success/', 
            cancel_url='http://127.0.0.1:8000/cancel/'
        )
    return checkout_session

def index(request):
    """Вывод каталога товаров из БД"""
    data = Item.objects.all()
    #for item in data:
        #price_usd = convert('rub', 'usd', price)
    return render(request, 'payment/index.html', {'data': data, 'user': user})# 'price_usd': price_usd

def get_item(request, item_id: int):
    """Вывод информации о выбранном товаре"""
    if request.method == 'POST':
        item_id = int(request.POST.get('item'))
        item = Item.objects.get(pk=item_id)
        user_cart = Order.objects.get(user=user)
        user_cart.items.add(item)
        return HttpResponse('Товар добавлен в корзину')
    else:
        try:
            item = Item.objects.get(pk=item_id)
        except Item.DoesNotExist:
            raise Http404(f'Товара с id={item_id} не существует')
        return render(request, 'payment/item.html', {'item': item})

def buy_item(request, order_id: int):
    """Отправка запроса Stripe на получение session_id"""
    order = Order.objects.get(pk=order_id)
    discount = order.discount
    tax = order.tax.tax
    items = order.items.all()
    # stripe.Customer.create_tax_id(
    #     "cus_NZKoSNZZ58qtO0",
    #     type="eu_vat",
    #     value="DE123456789",
    # )
    
    
    line_items = []
    for item in items:
        line_items.append({'price_data': {'currency': item.currency,
                                    'product_data': {'name': item.name, 'description': item.description or None}, 
                                    'unit_amount': int(item.price * 100)}, 'quantity': 1})

    has_coupon(discount)
    checkout_session = create_session(line_items, order, discount)
        
    return JsonResponse({'id': checkout_session.id})

def success(request):
    """Ответ при успешной оплате"""
    return HttpResponse('Оплата произошла успешно')

def cancel(request):
    """Ответ при неуспешной оплате"""
    return HttpResponse('Оплата была отменена')

def cart(request, user_name: str):
    order = Order.objects.get(user=user_name)
    user_items = order.items.all()
    amount = 0
    for item in user_items:
        amount += item.price
        currency = item.currency
    if order.discount:
        discount = round(amount * order.discount.discount / 100, 2)
    else:
        discount = 0
    total = amount - discount
    return render(request, 'payment/cart.html', {
        'user_cart': order, 
        'user_items': user_items, 
        'amount': amount, 
        'currency': currency,
        'total': total,
        'discount': discount,
        'publish_key': publish_key
    })