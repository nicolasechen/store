# mainapp/views.py
from django.shortcuts import render
from datetime import datetime
from .forms import *

# Create your views here.
def get_index(request):


    return render(request, 'index.html',locals())


def ajax_api(request):
    if request.method == 'GET':
        form = CategoryForm
        return render(request, 'ajax.html', locals())

    return