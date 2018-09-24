from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField('Category', max_length=20)

    def __str__(self):
        return self.name


class Item(models.Model):
    category = models.ForeignKey(Category)
    name = models.CharField('Name', max_length=20, unique=True)
    price = models.FloatField('Price', default=0)

    def __str__(self):
        return self.name


class Buying(models.Model):
    date = models.DateField(auto_now_add=True)
    item = models.ForeignKey(Item)
    cost = models.FloatField('Price for Buy', default=1)
    # How many set for buy?
    qty_buy = models.IntegerField('QTY for Buy', default=1)
    # How many items per set?
    qty_set = models.IntegerField('QTY for Set', default=1)


    # def __str__(self):
    #     return str(self.date) & "-" & str(self.item.name) & '-' & str(self.cost)
