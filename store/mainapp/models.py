from django.db import models
from django.utils import timezone


class Category(models.Model):
    name = models.CharField('Category', max_length=20)

    def __str__(self):
        return self.name


class Item(models.Model):
    category = models.ForeignKey(Category)
    name = models.CharFieldield('Name', max_length=20, unique=True)
    price = models.IntegerField('Price', default=0)

    def __str__(self):
        return self.name

class Inventory(models.Model):
    item = models.ForeignKey(Item)

    def __str__(self):
            return self.name
class Buying(models.Model):
    date = models.DateField(auto_now_add=True)


    def __str__(self):
        return
