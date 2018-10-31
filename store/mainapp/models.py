from django.db import models
from django.utils import timezone


def averagenum(num):
    nsum = 0
    for i in range(len(num)):
        nsum += num[i]
    return nsum / len(num)


class Category(models.Model):
    name = models.CharField('Category', max_length=20, )

    def __str__(self):
        return self.name


class Item(models.Model):
    category = models.ForeignKey(Category)
    name = models.CharField('Name', max_length=20, unique=True)
    price = models.FloatField('Price', default=0)
    cost = models.FloatField('Cost', default=0)
    cost_updated_at = models.DateTimeField(default=timezone.now)
    stock = models.IntegerField('Stock', default=0)
    stock_updated_at = models.DateTimeField(default=timezone.now)
    is_sell = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def update_cost(self):
        try:
            buys = self.buying_set.all()
        except Buying.DoesNotExist:
            return False
        if buys.count() > 0:
            all_cost_each_list = []

            for b in buys:
                # print(b)
                all_cost_each_list.append(b.cost / (b.qty_buy * b.qty_set))
            # print(all_cost_each_list)
            cost_each = round(averagenum(all_cost_each_list) * 100) / 100.00
            self.cost = cost_each
            self.cost_updated_at = timezone.now()
            self.save(update_fields=['cost', 'cost_updated_at'])
            return True

        return False

    def get_cost_avg(self):
        # print(self.buying_set.all())
        return self.cost

    def update_stock(self, qty):
        self.stock = self.stock + qty
        self.stock_updated_at = timezone.now()
        self.save(update_fields=['stock', 'stock_updated_at'])
        return True

    def get_stock(self):
        return self.stock


class Vendor(models.Model):
    name = models.CharField('Vender', max_length=10)

    def __str__(self):
        return self.name


class BuyingOrder(models.Model):
    date = models.DateField(default=timezone.now)
    vendor = models.ForeignKey(Vendor)

    def __str__(self):
        return str(self.date) + '-' + str(self.vendor)

    def get_total(self):
        from django.db.models import Sum
        sum = self.buying_set.aggregate(Sum('cost'))['cost__sum']
        if sum is None:
            return 0

        return sum


class Buying(models.Model):
    buying_order = models.ForeignKey(BuyingOrder)
    item = models.ForeignKey(Item)
    cost = models.FloatField('Price for Buy', default=1)
    # How many set for buy?
    qty_buy = models.IntegerField('QTY for Buy', default=1)
    # How many items per set?
    qty_set = models.IntegerField('QTY for Set', default=1)

    def get_qty_all(self):
        return self.qty_buy * self.qty_set

    def get_cost_each(self):
        return round((self.cost / (self.get_qty_all()) * 100)) / 100.00

    def get_subtotal(self):
        return self.cost * self.qty_buy


class Cashier(models.Model):
    date = models.DateTimeField(default=timezone.now)
    amount = models.IntegerField('Money', default=0)


class Selling(models.Model):
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=timezone.now)
    item = models.ForeignKey(Item)
    price = models.FloatField(default=1)
    cost = models.FloatField(default=1)
    qty = models.IntegerField(default=1)
