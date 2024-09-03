from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator




class Item(models.Model):  
    CURRENCIES = {
        'rub': 'rub',
        'usd': 'usd'
    }
         
    name = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name='Стоимость')
    currency = models.CharField(max_length=3, choices=CURRENCIES, default='rub', verbose_name='Валюта')
    
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
    
    name = models.CharField(max_length=100, default='default', verbose_name='Купон')
    duration = models.CharField(max_length=4, choices=DURATION, default='once', verbose_name='Продолжительность')
    discount = models.DecimalField(
        default=0.01,
        max_digits=4, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))], 
        verbose_name='Скидка в %'
    )

    def __str__(self) -> str:
        return f'{self.discount}%'
    
    class Meta:
        verbose_name = 'Скидка'
        verbose_name_plural = 'Скидки'
    

class Tax(models.Model):
    tax = models.DecimalField(
        db_index=True,
        unique=True,
        default=13.00,
        max_digits=4, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00'))], 
        verbose_name='Налог в %'
    )
    
    def __str__(self) -> str:
        return f'{self.tax}%'
    
    class Meta:
        verbose_name = 'Налог'
        verbose_name_plural = 'Налоги'
    
        
class Order(models.Model):
    user = models.CharField(max_length=100, verbose_name='Покупатель')
    items = models.ManyToManyField(Item, blank=True, related_name='order', verbose_name='Товар')
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
        default=1,
        on_delete=models.SET_DEFAULT, 
        related_name='order_tax',
        verbose_name='Налог'
    )
    
    def __str__(self) -> str:
        return f'Корзина пользователя {self.user}'
    
    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'