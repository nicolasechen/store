# mainapp/views.py
from django.shortcuts import render
from datetime import datetime

# Create your views here.
def get_index(request):


    return render(request, 'index.html',locals())
