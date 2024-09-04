from django.http import JsonResponse, Http404, HttpResponseBadRequest
from django.shortcuts import render
from django.utils.text import slugify
import stripe

from .models import Item, Order, Discount, OrderItems, Tax

from API_Stripe.settings import STRIPE_PUBLISHABLE_KEY as publish_key,\
    STRIPE_SECRET_KEY as secret_key, STRIPE_VERSION as version


stripe.api_key = secret_key
stripe.api_version = version


def has_or_create_coupon(discount: Discount) -> stripe._coupon.Coupon:
    """Проверка существования купона в Stripe, если не найден - создается"""
    if discount:
        for coupon in stripe.Coupon.list()['data']:
            if discount.name == coupon['id']:
                break
        else:
            coupon = stripe.Coupon.create(
                duration=discount.duration,
                id=discount.name,
                percent_off=discount.discount,
            )
    return coupon
            
def has_or_create_tax(tax_rate: Tax) -> stripe._tax_rate.TaxRate:
    """Проверка существования налога в Stripe, если не найден - создается"""
    if tax_rate:
        for tax in stripe.TaxRate.list()['data']:
            if tax_rate.name == tax['display_name']:
                break
        else:
            tax = stripe.TaxRate.create(
                display_name=tax_rate.name,
                percentage=tax_rate.tax,
                inclusive=tax_rate.inclusive,
                country=tax_rate.country,
            )
    return tax

def create_session(line_items: list[dict], 
                   order: Order, 
                   discount: stripe._coupon.Coupon
                   ) -> stripe.checkout._session.Session:
    """Создание платежной сессии"""
    user_name = order.user

    if discount:
        discounts = [{'coupon': discount.id}]
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
            success_url=f'http://127.0.0.1:8000/success/{user_name}', 
            cancel_url='http://127.0.0.1:8000/cancel/'
        )
    return checkout_session


def index(request):
    """Вывод каталога товаров из БД"""
    data = Item.objects.all()
    user = Order.objects.get(pk=1).user # Для всех покупок используется покупатель c id=1
    return render(request, 'payment/index.html', {'data': data, 'user': user})


def get_item(request, item_id: int):
    """Вывод информации о выбранном товаре и добавление его в корзину"""
    user = Order.objects.get(pk=1).user # Для всех покупок используется покупатель c id=1
    
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity')) # получаем кол-во товаров для добавления в корзину
        except ValueError:
            quantity = 1
        if quantity <= 0:
            return HttpResponseBadRequest('Значение должно быть больше 0')
        
        item = Item.objects.get(pk=item_id)
        order = Order.objects.get(user=user)
        
        # если в корзине есть товары, определяем основную валюту корзины
        if order.item.all(): 
            order_currency = Item.objects.get(pk=order.item.all()[0].item_id).currency
            
            # если товар имеет другую валюту - не попадает в корзину
            if item.currency != order_currency: 
                return render(request,
                              'payment/status.html',
                              {'response': 
                                      'Валюта товара не совпадает с валютой товаров в корзине'})
        
        order_item, created = OrderItems.objects.get_or_create(order=order, item=item)
        if not created: # если товар есть в корзине добавляем указанное количество 
            order_item.quantity += quantity
        else: # иначе создаем новый товар с указанным количеством
            order_item.quantity = quantity
        order_item.save()
        return render(request, 'payment/status.html', {'response': 'Товар добавлен в корзину'})
    
    # Вывод информации о товаре
    else: 
        try:
            item = Item.objects.get(pk=item_id)
        except Item.DoesNotExist:
            raise Http404(f'Товара с id={item_id} не существует')
        return render(request, 'payment/item.html', {'item': item}) 

def buy_item(request, order_id: int):
    """Отправка запроса Stripe на получение session_id и его передача на фронтенд"""
    order = Order.objects.get(pk=order_id)
    discount_model = order.discount
    tax_rate_model = order.tax
    items = order.item.all()
    
    # Проверка на существование купона и налога в Stripe
    tax_rate = has_or_create_tax(tax_rate_model)
    discount = has_or_create_coupon(discount_model)

    line_items = []
    
    # Создаем список товаров для передачи Stripe
    for item in items:
        quantity = item.quantity
        item = Item.objects.get(pk=item.item_id)
        line_items.append({'price_data': {'currency': item.currency,
                                    'product_data': {
                                        'name': item.name, 
                                        'description': item.description or None
                                    }, 
                                    'unit_amount': int(item.price * 100)},
                           'tax_rates': [tax_rate.id], 'quantity': quantity})

    checkout_session = create_session(line_items, order, discount)
    
    return JsonResponse({'id': checkout_session.id})

def success(request, user_name):
    """Ответ при успешной оплате и очищение корзины"""
    OrderItems.objects.filter(order__user=user_name).delete()
    return render(request, 'payment/status.html', {'response': 'Оплата произошла успешно'})

def cancel(request):
    """Ответ при неудачной оплате"""
    return render(request, 'payment/status.html', {'response': 'Оплата была отменена'})

def cart(request, user_name: str):
    """Корзина пользователя"""
    order = Order.objects.get(user=user_name)
    user_items = [(Item.objects.get(pk=order_item.item_id), order_item.quantity) \
        for order_item in order.item.all()]
    tax_rate = order.tax
    amount = 0
    
    # Если в корзине есть товары подсчитываем сумму с учетом скидки и налога
    if user_items:
        currency = user_items[0][0].currency

        for item, quantity in user_items:
            amount += item.price * quantity
            
        if order.discount:
            discount = round(amount * order.discount.discount / 100, 2)
        else:
            discount = 0
            
        total = amount - discount 
        
        if tax_rate:
            tax = round(total * tax_rate.tax / 100, 2)
        else:
            tax = 0
            
        total += tax
        
        return render(request, 'payment/cart.html', {
            'user_cart': order, 
            'user_items': user_items, 
            'amount': amount, 
            'currency': currency,
            'total': total,
            'tax_rate': tax_rate,
            'tax': tax,
            'discount': discount,
            'publish_key': publish_key
        })
    else:
        return render(request, 'payment/status.html', {'response': 'Корзина пустая'})
    
def delete_order(request, user_name: str):
    """Очищение корзины"""
    OrderItems.objects.filter(order__user=user_name).delete()
    return render(request, 'payment/status.html', {'response': 'Корзина очищена'})