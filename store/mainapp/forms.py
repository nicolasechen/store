from django import forms
from .models import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, HTML
from crispy_forms.bootstrap import FieldWithButtons, StrictButton
from django.forms import BaseModelFormSet, BaseInlineFormSet, BaseFormSet
from django.forms.models import modelformset_factory, inlineformset_factory, formset_factory


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name',)

    def __init__(self, *args, submit_title="Save", **kwargs, ):
        super().__init__(*args, **kwargs)
        field_text = [
            ('name', 'Category', 'Category of Items.'),
        ]
        for x in field_text:
            self.fields[x[0]].label = x[1]
            self.fields[x[0]].help_text = x[2]
            self.fields[x[0]].widget.attrs['class'] = 'form-control-sm'

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.help_text_inline = True
        self.helper.layout = Layout(
            Div(
                Div('name', css_class='col'),
            )
        )
        self.helper.add_input(Submit('submit', submit_title))


class Base_OPTIONS_FormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_method = 'post'
        self.form_tag = False
        self.disable_csrf = True
        self.form_show_errors = True

        self.layout = Layout(
            Div(
                Div('id'),
                Div('name', css_class='col-2'),
                Div('DELETE', css_class='col-2'),
                css_class='row'
            )
        )


class Label_Base_OPTIONS_FormSet(BaseModelFormSet):
    def add_fields(self, form, index):
        super(Label_Base_OPTIONS_FormSet, self).add_fields(form, index)
        form.fields['name'] = forms.CharField(label='', required=True, widget=forms.TextInput(), max_length=20, )
        form.fields['name'].widget.attrs['class'] = 'form-control-sm'

    def get_queryset(self):
        return super(Label_Base_OPTIONS_FormSet, self).get_queryset().order_by('name')


Base_Category_FormSet = modelformset_factory(
    model=Category,
    fields=('name', 'id',),
    extra=1,
    can_delete=True,
    formset=Label_Base_OPTIONS_FormSet,
)


class Category_FormSet(Base_Category_FormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = Base_OPTIONS_FormSetHelper()


Base_Vendor_FormSet = modelformset_factory(
    model=Vendor,
    fields=('name', 'id',),
    extra=1,
    can_delete=True,
    formset=Label_Base_OPTIONS_FormSet,
)


class Vendor_FormSet(Base_Vendor_FormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = Base_OPTIONS_FormSetHelper()


class Label_Base_ITEMS_Formset(BaseInlineFormSet):
    def add_fields(self, form, index):
        super(Label_Base_ITEMS_Formset, self).add_fields(form, index)
        form.fields['name'] = forms.CharField(label='', required=True, widget=forms.TextInput(), max_length=20, )
        form.fields['name'].widget.attrs['class'] = 'form-control-sm ipt-item'
        form.fields['price'] = forms.FloatField(label='', required=True, widget=forms.TextInput(), )
        form.fields['price'].widget.attrs['class'] = 'form-control-sm ipt-price'
        # form.fields['price'].widget.attrs['value'] = '0'

        my_fields = ['cost', 'profit', 'stock']
        for f in my_fields:
            form.fields[f] = forms.CharField(label='', disabled=True, widget=forms.TextInput(), required=False)
            form.fields[f].widget.attrs['class'] = 'form-control-sm input_to_label ml-3'

        try:
            cost_avg = self.queryset[index].get_cost_avg()
        except IndexError:
            cost_avg = ''
        form.fields['cost'].widget.attrs['value'] = cost_avg

        try:
            stock = self.queryset[index].get_stock()
        except IndexError:
            stock = ''
        form.fields['stock'].widget.attrs['value'] = stock
        form.fields['is_sell'].label = 'Sell'


Base_Item_Formset = inlineformset_factory(
    parent_model=Category,
    model=Item,
    fields=('id', 'name', 'price', 'is_sell'),
    extra=1,
    fk_name='category',
    can_delete=True,
    formset=Label_Base_ITEMS_Formset,
)


class Item_Formset(Base_Item_Formset):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = Base_OPTIONS_FormSetHelper()
        self.helper.layout = Layout(
            Div(
                Div('id'),
                Div('name', css_class='col-2'),
                Div('price', css_class='col-1'),
                Div('cost', css_class='col-1'),
                Div('profit', css_class='col-1'),
                Div('stock', css_class='col-1'),
                Div('is_sell', css_class='col-1'),
                Div('DELETE', css_class='col-1'),
                css_class='row'
            )
        )


# class Label_Base_Buying_Formset(BaseFormSet):
#     def add_fields(self, form, index):
#         super(Label_Base_Buying_Formset, self).add_fields(form, index)
#         form.fields['item'] = forms.CharField(label='', required=True, widget=forms.TextInput(), max_length=20, )
#         form.fields['item'].widget.attrs['class'] = 'form-control-sm'
#         form.fields['cost'] = forms.FloatField(label='', required=True, widget=forms.TextInput(), )
#         form.fields['cost'].widget.attrs['class'] = 'form-control-sm'
#         form.fields['qty_buy'] = forms.IntegerField(label='', required=True, widget=forms.TextInput(), )
#         form.fields['qty_buy'].widget.attrs['class'] = 'form-control-sm'
#         form.fields['qty_set'] = forms.IntegerField(label='', required=True, widget=forms.TextInput(), )
#         form.fields['qty_set'].widget.attrs['class'] = 'form-control-sm'

def get_items_selection1():
    category = Category.objects.order_by('name').all()
    opt_list = ''
    for c in category:
        opt_list += '<optgroup label="{category_name}"></optgroup>'.format(
            category_name=c.name
        )
        item = Item.objects.filter(category=c, is_sell=True).order_by('name').all()
        for i in item:
            opt_list += '<option value="{item_pk}">{item_name}</option>'.format(
                item_pk=i.pk,
                item_name=i.name,
            )
    return '<select name="item" class="select form-control form-control-sm">' + opt_list + '</select>'


def get_items_selection(empty_label=False):
    list = []
    if empty_label:
        list.append(['', '---------'])
    category = Category.objects.order_by('name').all()
    for c in category:
        list_i = []
        item = Item.objects.filter(category=c, is_sell=True).order_by('name').all()
        for i in item:
            list_i.append([i.pk, i.name])
        list.append([c.name, list_i])
    return list


class Base_Buying_Form(forms.Form):
    # item = forms.CharField(label='', required=True, widget=forms.TextInput(), max_length=20, )
    item = forms.ChoiceField(choices=get_items_selection(), label='')
    cost = forms.FloatField(label='', required=True, widget=forms.TextInput(), )
    qty_buy = forms.IntegerField(label='', required=True, widget=forms.TextInput(), )
    qty_set = forms.IntegerField(label='', required=True, widget=forms.TextInput())
    total_of_buy = forms.CharField(label='', disabled=True, widget=forms.TextInput(), required=False)
    cost_of_each = forms.CharField(label='', disabled=True, widget=forms.TextInput(), required=False)
    subtotal = forms.CharField(label='', disabled=True, widget=forms.TextInput(), required=False)
    no = forms.CharField(label='', disabled=True, widget=forms.TextInput(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        my_fields = ['item', 'cost', 'qty_buy', 'qty_set', 'subtotal', 'no']
        for f in my_fields:
            self.fields[f].widget.attrs['class'] = 'form-control-sm ipt_field'
        self.fields['cost_of_each'].widget.attrs['class'] = 'form-control-sm input_to_label'
        self.fields['total_of_buy'].widget.attrs['class'] = 'form-control-sm input_to_label'
        self.fields['subtotal'].widget.attrs['class'] = 'form-control-sm input_to_label ipt_subtotal'
        self.fields['no'].widget.attrs['class'] = 'form-control-sm input_to_label_white ipt_no'
        self.fields['qty_set'].widget.attrs['class'] = 'form-control-sm ipt_field ipt_qty_set'
        self.fields['qty_set'].widget.attrs['value'] = '1'


Base_Buying_Formset = formset_factory(
    extra=1,
    form=Base_Buying_Form,
)


class Buying_Formset(Base_Buying_Formset):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            Div(
                Div('no', css_class='col-1'),
                Div('item', css_class='col-4'),
                Div('cost', css_class='col-2'),
                Div('qty_buy', css_class='col-1'),
                Div('qty_set', css_class='col-1'),
                Div('cost_of_each', css_class='col-1'),
                Div('total_of_buy', css_class='col-1'),
                Div('subtotal', css_class='col-1'),
                css_class='row'
            )
        )


class Base_Buying_Form_B(forms.Form):
    item = forms.CharField(label='', required=True, widget=forms.TextInput(), max_length=20, )
    cost = forms.FloatField(label='', required=True, widget=forms.TextInput(), )
    qty_buy = forms.IntegerField(label='', required=True, widget=forms.TextInput(), )
    qty_set = forms.IntegerField(label='', required=True, widget=forms.TextInput(), )


Base_Buying_Formset_B = formset_factory(
    extra=1,
    form=Base_Buying_Form_B,
)


class Buying_Formset_B(Base_Buying_Formset_B):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            Div(
                Div('id'),
                Div('item', css_class='col-2'),
                Div('cost', css_class='col-1'),
                Div('qty_buy', css_class='col-1'),
                Div('qty_set', css_class='col-1'),
                css_class='row'
            )
        )


class BuyingOrderForm(forms.ModelForm):
    class Meta:
        model = BuyingOrder
        fields = ('date', 'vendor')

    def __init__(self, *args, **kwargs, ):
        super().__init__(*args, **kwargs)
        field_text = [
            ('date', 'Date', 'Date of Buying'),
            ('vendor', 'Vendor', 'Where to buy'),
        ]
        for x in field_text:
            self.fields[x[0]].label = x[1]
            self.fields[x[0]].help_text = x[2]
            self.fields[x[0]].widget.attrs['class'] = 'form-control-sm'

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.label_class = 'font-weight-bold'
        self.helper.layout = Layout(
            Div(
                Div(FieldWithButtons('date',
                                     StrictButton('<i class="far fa-calendar-alt"></i>', css_class='btn-sm btn-date')
                                     , css_class='form-control-sm'),
                    css_class='col-2'),
                Div(
                    Div('vendor', css_class='col-10'),
                    Div(HTML('<i class="fas fa-pen-square"></i> <i class="fas fa-plus-square"></i>'),
                        css_class='col-2 pt-3 mt-4 h6 text-secondary'),
                    css_class='form-row col-3'),
                css_class='row'
            )
        )


class Base_Selling_Form(forms.Form):
    item = forms.ChoiceField(choices=get_items_selection(empty_label=True), label='')
    # cost = forms.FloatField(label='', required=False, widget=forms.TextInput(), )
    qty = forms.IntegerField(label='', required=True, widget=forms.TextInput(), )
    price = forms.CharField(label='', disabled=True, widget=forms.TextInput(), required=False)
    subtotal = forms.CharField(label='', disabled=True, widget=forms.TextInput(), required=False)
    no = forms.CharField(label='', disabled=True, widget=forms.TextInput(), required=False)
    stock = forms.CharField(label='', disabled=True, widget=forms.TextInput(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        my_fields = ['item', 'qty', ]
        for f in my_fields:
            self.fields[f].widget.attrs['class'] = 'form-control-sm ipt_field'
        self.fields['item'].widget.attrs['class'] = 'form-control-sm ipt_field ipt_item'
        self.fields['price'].widget.attrs['class'] = 'form-control-sm input_to_label'
        self.fields['subtotal'].widget.attrs['class'] = 'form-control-sm input_to_label ipt_subtotal'
        self.fields['no'].widget.attrs['class'] = 'form-control-sm input_to_label_white ipt_no'
        self.fields['qty'].widget.attrs['value'] = '1'
        self.fields['stock'].widget.attrs['class'] = 'form-control-sm input_to_label ipt_stock'


Base_Selling_Formset = formset_factory(
    extra=1,
    form=Base_Selling_Form,
)


class Selling_Formset(Base_Selling_Formset):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.layout = Layout(
            Div(
                Div('no', css_class='col-2'),
                Div('item', css_class='col-4'),
                Div('qty', css_class='col-1'),
                Div('price', css_class='col-1'),
                Div('subtotal', css_class='col-1'),
                Div(HTML(''), css_class='col-1'),
                Div('stock', css_class='col-1'),

                css_class='row'
            )
        )


class Selling_Date_Form(forms.Form):
    date = forms.DateField(label='Date')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget.attrs['class'] = 'form-control-sm'
        self.fields['date'].widget.attrs['style'] = 'text-align: center;'
        self.fields['date'].widget.attrs['value'] = timezone.now().strftime('%Y-%m-%d')
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-3 h5'
        self.helper.field_class = 'col-6'
        self.helper.layout = Layout(
            Div(FieldWithButtons('date',
                                 StrictButton('<i class="far fa-calendar-alt"></i>', css_class='btn-sm btn-date')
                                 , css_class='form-control-sm'),
                css_class='col-4 p-0 mt-3'),
        )


class Opening_Form(forms.ModelForm):
    class Meta:
        model = Cashier
        fields = ('date', 'amount')

    date = forms.DateField(label='Date')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['amount'].widget.attrs['class'] = 'form-control-sm'
        self.fields['amount'].widget.attrs['style'] = 'text-align: right;'
        self.fields['date'].widget.attrs['class'] = 'form-control-sm'
        self.fields['date'].widget.attrs['style'] = 'text-align: center;'
        self.fields['date'].widget.attrs['value'] = timezone.now().strftime('%Y-%m-%d')
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        self.helper.disable_csrf = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-4 h5'
        self.helper.field_class = 'col-8'
        self.helper.layout = Layout(
            FieldWithButtons('date',
                             StrictButton('<i class="far fa-calendar-alt"></i>', css_class='btn-sm btn-date')
                             , css_class='form-control-sm'),
            Div('amount', css_class='form-control-sm'),
        )


class Selling_Change_Form(forms.ModelForm):
    class Meta:
        model = Selling
        fields = ('price', 'cost', 'qty')

    item = forms.ChoiceField(choices=get_items_selection(), label='Item')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        my_fields = ('item', 'price', 'cost', 'qty')
        for f in my_fields:
            self.fields[f].widget.attrs['class'] = 'form-control-sm'
        self.fields['price'].label = 'Price/Each'
        self.fields['cost'].label = 'Cost/Each'
        self.fields['cost'].required = False
        self.fields['cost'].help_text = ' If no need, do not to change.'
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.label_class = 'h6'
        self.helper.layout = Layout(
            Div(
                Div('item', css_class='col-9'),
                Div('qty', css_class='col-3'), css_class='form-row'
            ),
            Div(
                Div('price', css_class='col-6'),
                Div('cost', css_class='col-6'), css_class='form-row border p-2 m-1'
            )
        )


class Buying_Form(forms.ModelForm):
    class Meta:
        model = Buying
        fields = ('cost', 'qty_buy', 'qty_set')

    item = forms.ChoiceField(choices=get_items_selection(), label='Item')
    qty_of_stock = forms.CharField(label='QTY/Stock', disabled=True, widget=forms.TextInput(), required=False)
    cost_of_each = forms.CharField(label='Cost/Each', disabled=True, widget=forms.TextInput(), required=False)
    subtotal = forms.CharField(label='Total Cost', disabled=True, widget=forms.TextInput(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        my_fields = ['item', 'cost', 'qty_buy', 'qty_set', 'subtotal']
        for f in my_fields:
            self.fields[f].widget.attrs['class'] = 'form-control-sm ipt_field'
        self.fields['cost'].label = 'Cost'
        self.fields['cost'].help_text = 'Price of buy'
        self.fields['cost_of_each'].widget.attrs['class'] = 'form-control-sm input_to_label'
        self.fields['qty_of_stock'].widget.attrs['class'] = 'form-control-sm input_to_label'
        self.fields['subtotal'].widget.attrs['class'] = 'form-control-sm input_to_label ipt_subtotal'
        self.fields['qty_set'].widget.attrs['class'] = 'form-control-sm ipt_field ipt_qty_set'
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.label_class = 'h6'
        self.helper.layout = Layout(
            Div(
                Div('item', css_class='col-9'),
                Div('cost', css_class='col-3'), css_class='form-row'
            ),
            Div(
                Div('qty_buy', css_class='col-6'),
                Div('qty_set', css_class='col-6'), css_class='form-row'
            ),
            Div(
                Div('cost_of_each', css_class='col-4'),
                Div('qty_of_stock', css_class='col-4'),
                Div('subtotal', css_class='col-4'),
                css_class='form-row'
            )
        )
