from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator


class Item(models.Model):  
    CURRENCIES = {
        'rub': 'руб',
        'usd': 'USD'
    }
         
    name = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))], 
        verbose_name='Стоимость'
        )
    currency = models.CharField(
        max_length=3, 
        choices=CURRENCIES, 
        default='rub', 
        verbose_name='Валюта', 
        )
    
    def __str__(self) -> str:
        return self.name
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['name']
        indexes = [models.Index(fields=['name'])]
        
    
    
class Discount(models.Model):
    DURATION = {
        'frv': 'forever',
        'once': 'once',
        'rpt': 'repeating'
    }
    
    name = models.CharField(max_length=100, unique=True, verbose_name='Название купона')
    duration = models.CharField(max_length=4, choices=DURATION, default='once', verbose_name='Продолжительность')
    discount = models.DecimalField(
        default=0.01,
        max_digits=4, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))], 
        verbose_name='Скидка в %'
    )

    def __str__(self) -> str:
        return f'Купон {self.name} на {self.discount}%, продолжительностю {self.DURATION[self.duration]}'
    
    class Meta:
        verbose_name = 'Скидка'
        verbose_name_plural = 'Скидки'
    

class Tax(models.Model):
    name = models.CharField(max_length=100, default='НДС', verbose_name='Название налога')
    inclusive = models.BooleanField(
        default=False, 
        verbose_name='Инклюзивная ставка', 
        help_text='Указывает, является ли ставка налога инклюзивной или эксклюзивной')
    country = models.CharField(
        max_length=2, 
        default='RU', 
        blank=True, 
        null=True, 
        verbose_name='Код страны', 
        help_text='(ISO 3166-1 alpha-2)')
    tax = models.DecimalField(
        default=0.01,
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Налог в %'
    )
    
    def __str__(self) -> str:
        return f'{self.name} - {self.tax}%'
    
    class Meta:
        verbose_name = 'Налог'
        verbose_name_plural = 'Налоги'
    
        
class Order(models.Model):
    user = models.CharField(max_length=100, unique=True, verbose_name='Покупатель', help_text='E-mail')
    discount = models.ForeignKey(
        Discount,
        blank=True,
        null=True,
        on_delete=models.SET_NULL, 
        related_name='order_disc', 
        verbose_name='Скидка'
    )
    tax = models.ForeignKey(
        Tax,
        blank=True,
        null=True,
        on_delete=models.SET_NULL, 
        related_name='order_tax',
        verbose_name='Налог'
    )
    
    def __str__(self) -> str:
        return f'Корзина пользователя {self.user}'
    
    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        

class OrderItems(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='item', verbose_name='Корзина')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='order', verbose_name='Товар')
    quantity = models.IntegerField(default=1, verbose_name='Количество')
    
    def __str__(self) -> str:
        return f'{self.order} c товаром {self.item} в количестве {self.quantity} шт.'
    
    class Meta:
        unique_together = ('order', 'item')
        verbose_name = 'Товар корзины'
        verbose_name_plural = 'Товары корзины'