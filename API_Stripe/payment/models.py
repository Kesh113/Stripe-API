from decimal import Decimal
from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator


class Item(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name='Стоимость')
    
    def __str__(self) -> str:
        return self.name
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['name']
        indexes = [models.Index(fields=['name'])]
        
    def get_absolute_url(self):
        return reverse('payment:item_detail', kwargs={'item_id': self.id})
    