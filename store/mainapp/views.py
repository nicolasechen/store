# mainapp/views.py
from django.shortcuts import render, redirect, reverse
from django.http import Http404, JsonResponse, HttpResponse, HttpResponseBadRequest
from .forms import *

from django.core.paginator import Paginator


# Create your views here.

def get_opening(date):
    try:
        return Cashier.objects.get(date__range=(date + ' 00:00:00', date + ' 23:59:59')).amount
    except Cashier.DoesNotExist:
        return None


# 取得URL的GET參數,移除某些reg
def get_url_GET(request, reg=r"&p=(\d+)"):
    import re
    return re.sub(reg, "", request.GET.urlencode())


def get_index(request):
    return redirect(reverse('selling') + '?t=cs')


def get_settings(request):
    # if request.method == 'GET':
    target = request.GET.get('t')
    # is_errs = request.GET.get('err')
    if target == 'category':
        obj_model = 'Category'
        obj_formset = 'Category_FormSet'

    elif target == 'vendor':
        obj_model = 'Vendor'
        obj_formset = 'Vendor_FormSet'

    elif target == 'items':
        cpk = request.GET.get('cpk')  # Category PK
        obj_model = 'Item'
        obj_formset = 'Item_Formset'
        try:
            obj_category = Category.objects.get(pk=cpk)
        except Category.DoesNotExist:
            raise Http404
    else:
        raise Http404

    if request.method == 'POST':
        formset = eval('{obj_formset}(request.POST)'.format(obj_formset=obj_formset))
        if target == 'items':
            formset = eval('{obj_formset}(request.POST,instance=obj_category)'.format(obj_formset=obj_formset))

            if cpk is not None:
                url_cpk = '&cpk=' + cpk
            else:
                url_cpk = ''

            if formset.is_valid():
                ii = formset.save(commit=False)
                for i in ii:
                    i.save()
                for obj in formset.deleted_objects:
                    obj.delete()
                return redirect(reverse('settings') + '?act=1&t=' + target + url_cpk)
            print(formset.total_error_count())

    formset = eval('{obj_formset}()'.format(obj_formset=obj_formset))
    if target == 'items':
        formset = eval('{obj_formset}(instance=obj_category)'.format(obj_formset=obj_formset))

    categorys = Category.objects.order_by('name').all()
    categorys_list = []
    for category in categorys:
        categorys_list.append((category.name, str(category.pk)))

    return render(request, 'settings.html', locals())


def get_buying(request):
    target = request.GET.get('t')
    if request.method == 'GET':
        if target == 'bl':
            cur_page = request.GET.get('p')
            if cur_page is None:
                cur_page = 1
            else:
                try:
                    cur_page = int(cur_page)
                except TypeError:
                    raise Http404

            bos = BuyingOrder.objects.order_by('-date', '-pk').all()

            pages = Paginator(bos, 20)
            try:
                bos = pages.page(cur_page)
            except:
                bos = pages.page(1)

            url_get = get_url_GET(request)

            return render(request, 'buying_list.html', locals())

        elif target == 'bn':
            formset = Buying_Formset()
            form = BuyingOrderForm()
            return render(request, 'buying_create.html', locals())

        elif target == 'od':
            opk = request.GET.get('opk')  # buyingorder pk
            cur_page = request.GET.get('p')

            if cur_page is None:
                cur_page = 1
            else:
                try:
                    cur_page = int(cur_page)
                except TypeError:
                    raise Http404

            try:
                objs = BuyingOrder.objects.get(pk=opk)
            except BuyingOrder.DoesNotExist:
                raise Http404

            items = Buying.objects.filter(buying_order=opk).order_by('pk').all()
            pages = Paginator(items, 20)
            try:
                items = pages.page(cur_page)
            except:
                items = pages.page(1)
            url_get = get_url_GET(request)

            return render(request, 'buying_detail.html', locals())

        else:
            raise Http404
    elif request.method == 'POST':
        if target == 'bn':
            form = BuyingOrderForm(request.POST)
            formset = Buying_Formset(request.POST)
            if form.is_valid() and formset.is_valid():
                bo = form.save(commit=True)
                for f in formset:
                    data = f.cleaned_data
                    items = Item.objects.get(pk=data['item'])
                    new_buy = Buying()
                    new_buy.buying_order = bo
                    new_buy.item = items
                    new_buy.cost = data['cost']
                    new_buy.qty_buy = data['qty_buy']
                    new_buy.qty_set = data['qty_set']
                    new_buy.save()
                    items.update_cost()
                    items.update_stock(data['qty_buy'] * data['qty_set'])
                return redirect(reverse('buying') + '?t=bl')
            return render(request, 'buying_create.html', locals())
    return render(request, 'buying.html', locals())


def get_selling(request):
    target = request.GET.get('t')
    if request.method == 'GET':
        if target == 'cs':
            open_amount = get_opening(timezone.now().strftime('%Y-%m-%d'))
            form = Selling_Date_Form()
            formset = Selling_Formset()
        elif target == 'sl':
            date = request.GET.get('d')
            cur_page = request.GET.get('p')
            if cur_page is None:
                cur_page = 1
            else:
                try:
                    cur_page = int(cur_page)
                except TypeError:
                    raise Http404
            if date is None:
                date = timezone.now().strftime('%Y-%m-%d')
            try:
                sells = Selling.objects.filter(date=date).order_by('-date', '-time', '-pk').all()
            except:
                pass
            pages = Paginator(sells, 20)
            try:
                sells = pages.page(cur_page)
            except:
                sells = pages.page(1)

            total = {'income': 0, 'profit': 0}
            for s in sells:
                total['income'] = total['income'] + (s.qty * s.price)
                total['profit'] = total['profit'] + ((s.price - s.cost) * s.qty)

            url_get = get_url_GET(request)
            # print(timezone.now())
            return render(request, 'selling_list.html', locals())
        elif target == 'op':
            form = Opening_Form()
            return render(request, 'opening_amount.html', locals())
        else:
            raise Http404
    elif request.method == 'POST':
        if target == 'cs':
            form = Selling_Date_Form(request.POST)
            formset = Selling_Formset(request.POST)
            print(request.POST)
            if form.is_valid() and formset.is_valid():
                for f in formset:
                    data = f.cleaned_data
                    items = Item.objects.get(pk=data['item'])
                    sell = Selling()
                    sell.date = form.cleaned_data['date']
                    sell.item = items
                    sell.price = items.price
                    sell.cost = items.cost
                    sell.qty = data['qty']
                    sell.save()
                    items.update_stock((data['qty'] * -1))
                return redirect(reverse('selling') + '?t=cs')
            else:
                print(formset.errors)
        elif target == 'op':
            form = Opening_Form(request.POST)
            if form.is_valid():
                data = form.save()
                script = '<script type="text/javascript">window.opener.parent.location.reload();window.close();</script>'
                return HttpResponse(script)
        else:
            raise Http404
    return render(request, 'selling_cashier.html', locals())


def ajax_api(request):
    content = {}
    target = request.GET.get('t')

    if target == 'selling':
        if request.method == 'GET':
            act = request.GET.get('act')
            if act == '1':  # get-items-price
                ipk = request.GET.get('ipk')
                content = {
                    'price': str(Item.objects.get(pk=ipk).price),
                    'cost': str(Item.objects.get(pk=ipk).cost),
                    'stock': str(Item.objects.get(pk=ipk).get_stock())
                }
                return JsonResponse(content)


    elif target == 'selling-change':
        spk = request.GET.get('spk')
        try:
            se = Selling.objects.get(pk=spk)
        except Selling.DoesNotExist:
            return HttpResponseBadRequest()

        if request.method == 'GET':
            form = Selling_Change_Form(initial={'item': se.item.pk}, instance=se)
            return render(request, 'ajax.html', locals())

        elif request.method == 'POST':
            orig_se = Selling.objects.get(pk=spk)
            content = {}
            form = Selling_Change_Form(request.POST, instance=se)

            if form.is_valid():
                data = form.save(commit=False)

                data.item = Item.objects.get(pk=request.POST['item'])
                if orig_se.item != data.item:
                    # 復原原品項庫存
                    orig_se.item.update_stock(orig_se.qty)
                    # 更新新品項庫存
                    se.item.update_stock(data.qty * -1)
                if orig_se.item == data.item:
                    # 同品項 庫存調整
                    se.item.update_stock((data.qty * -1) + orig_se.qty)
                form.save()
                content = {
                    'is_success': True,
                }
            else:
                print(form.errors)
            return JsonResponse(content)

        elif request.method == 'DELETE':
            # 調整庫存數量
            se.item.update_stock(se.qty)
            se.delete()

            content = {
                'is_success': True,
            }
            return JsonResponse(content)

    elif target == 'buying-change':
        bpk = request.GET.get('bpk')

        try:
            buys = Buying.objects.get(pk=bpk)

        except Buying.DoesNotExist:
            return HttpResponseBadRequest()

        if request.method == 'GET':
            form = Buying_Form(initial={'item': buys.item.pk}, instance=buys)
            return render(request, 'ajax.html', locals())

        elif request.method == "POST":
            orig_buy = Buying.objects.get(pk=bpk)
            content = {}
            form = Buying_Form(request.POST, instance=buys)

            if form.is_valid():
                data = form.save(commit=False)
                data.item = Item.objects.get(pk=request.POST['item'])
                if orig_buy.item != data.item:
                    # 復原原品項庫存
                    orig_buy.item.update_stock((orig_buy.qty_buy * orig_buy.qty_set) * -1)
                    # 更新新品項庫存
                    data.item.update_stock(data.qty_buy * data.qty_set)
                if orig_buy.item == data.item:
                    # 同品項 庫存調整
                    buys.item.update_stock(((orig_buy.qty_buy * orig_buy.qty_set) * -1) + (data.qty_buy * data.qty_set))
                form.save()
                orig_buy.item.update_cost()
                buys.item.update_cost()
                content = {
                    'is_success': True,
                }
            else:
                print(form.errors)
            return JsonResponse(content)
        elif request.method == 'DELETE':
            # 調整庫存數量

            item = Item.objects.get(pk=buys.item.pk)
            item.update_stock(buys.qty_buy * buys.qty_set * -1)
            buys.delete()
            item.update_cost()

            script = '<script type="text/javascript">location.reload();</script>'
            content = {
                'is_success': True,
            }
            return JsonResponse(content)
    elif target == 'buying-order-change':
        if request.method == 'DELETE':
            bopk = request.GET.get('bopk')
            try:
                bo = BuyingOrder.objects.get(pk=bopk)
            except BuyingOrder.DoesNotExist:
                return HttpResponseBadRequest()

            # 分開刪除訂單下各商品並更新庫存與成本
            buys = Buying.objects.filter(buying_order=bo).all()
            for b in buys:
                i = Item.objects.get(pk=b.item.pk)
                # 調整庫存數量
                i.update_stock(b.qty_buy * b.qty_set * -1)
                b.delete()
                i.update_cost()

            bo.delete()

            content = {
                # 'url': reverse('buying') + '?t=bl',
                'is_success': True,
            }
        return JsonResponse(content)

    elif target == 'buying-order-add':
        bopk = request.GET.get('bopk')

        if request.method == 'GET':
            form = Buying_Form(initial={'cost':'','qty_buy':''})
            return render(request, 'ajax.html', locals())

        elif request.method == "POST":
            # orig_buy = Buying.objects.get(pk=bpk)
            content = {}
            form = Buying_Form(request.POST)

            if form.is_valid():
                data = form.save(commit=False)
                data.buying_order = BuyingOrder.objects.get(pk=bopk)
                data.item = Item.objects.get(pk=request.POST['item'])
                # if orig_buy.item != data.item:
                #     # 復原原品項庫存
                #     orig_buy.item.update_stock((orig_buy.qty_buy * orig_buy.qty_set) * -1)
                #     # 更新新品項庫存
                data.item.update_stock(data.qty_buy * data.qty_set)
                # if orig_buy.item == data.item:
                #     # 同品項 庫存調整
                #     buys.item.update_stock(((orig_buy.qty_buy * orig_buy.qty_set) * -1) + (data.qty_buy * data.qty_set))
                form.save()
                data.item.update_cost()
                # orig_buy.item.update_cost()
                # buys.item.update_cost()
                content = {
                    'is_success': True,
                }
            else:
                print(form.errors)
            return JsonResponse(content)
    else:
        return HttpResponseBadRequest()

    return
