from django import forms
from .models import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, HTML
from django.forms import BaseModelFormSet
from django.forms.models import modelformset_factory


class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ('name',)
