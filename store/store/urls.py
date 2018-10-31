"""store URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from mainapp.views import get_index, ajax_api, get_settings, get_buying, get_selling

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', get_index, name='home'),
    url(r'^api/$', ajax_api, name='api'),
    url(r'^settings/$', get_settings, name='settings'),
    url(r'^buying/$', get_buying, name='buying'),
    url(r'^selling/$', get_selling, name='selling'),

]
