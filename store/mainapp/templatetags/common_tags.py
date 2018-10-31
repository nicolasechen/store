# mainapp/templatetags/common_tags.py

from django import template
from django.core.urlresolvers import reverse, resolve

register = template.Library()
css_active_string = 'active'


@register.simple_tag
def is_active(request, *url_strings):
    for url_pattern in url_strings:
        if url_pattern in request.path:
            return css_active_string
    return ''


@register.simple_tag
def is_active_reverse(request, *url_names):
    for url_name in url_names:
        if reverse(url_name) in request.path:
            return css_active_string
    return ''


@register.simple_tag
def is_active_resolve(request, *url_names):
    resolver_match = resolve(request.path)
    for url_name in url_names:
        if resolver_match.url_name == url_name:
            return css_active_string
    return ''


@register.simple_tag
def is_active_get(request, *url_strings):
    # print(url_strings)
    for url_pattern in url_strings:
        if url_pattern in request.get_full_path():
            return css_active_string
    return ''


@register.filter()
def get_buyingorder_total(obj):
    return obj.get_total()


@register.filter()
def get_item_detail(obj, string):
    if string == 'each':
        return obj.get_cost_each()
    elif string == 'all':
        return obj.get_qty_all()
    elif string == 'subtotal':
        return obj.get_subtotal()
    else:
        return 0


@register.filter()
def get_sell_profit(obj):
    return obj.price - obj.cost


@register.filter()
def get_amount(request, string):
    from mainapp.models import Cashier, Selling
    from django.utils import timezone
    from django.db.models import Sum, F

    date = timezone.now().strftime('%Y-%m-%d')
    se = Selling.objects.filter(date=date).aggregate(t=Sum(F('price') * F('qty')))['t']
    if se is None: se = 0

    if string == "D":
        try:
            op = Cashier.objects.get(date__range=(date + ' 00:00:00', date + ' 23:59:59')).amount
        except Cashier.DoesNotExist:
            return 0
        return str(op + se)
    elif string == "I":
        return str(se)
    elif string == "P":
        co = Selling.objects.filter(date=date).aggregate(t=Sum(F('cost') * F('qty')))['t']
        if co is None: co = 0
        return str(round((se - co) * 100) / 100.00)
    return "0"


@register.filter()
def get_times(a1, a2):
    return a1 * a2


# 取得購買Order之詳細品項
@register.filter()
def get_buying_detail(bo):
    from mainapp.models import Buying
    try:
        buys = bo.buying_set.order_by('pk').all()
    except Buying.DoesNotExist:
        return None
    strList = ''

    for index in range(len(buys)):
        strList += str(buys[index].item) + ' x' + str((buys[index].qty_buy * buys[index].qty_set))
        # 如果不是最後一樣物品就加逗號
        if index != len(buys)-1:
            strList += ', '
    return strList
