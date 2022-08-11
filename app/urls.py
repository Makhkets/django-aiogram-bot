"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.decorators import user_passes_test
from django.urls import path, include
from django.shortcuts import render

from aviato.models import *

def get_report():
    expectation = Applications.objects.filter(status="Ожидание подтверждения").count()
    confirmed = Applications.objects.filter(status="Подтвержден").count()
    canceled = Applications.objects.filter(status="Отменен").count()
    transferred = Applications.objects.filter(status="Передан упаковщику").count()
    transferred_dispatcher = Applications.objects.filter(status="Упакован").count()
    drive = Applications.objects.filter(status="В дороге").count()
    delivered = Applications.objects.filter(status="Доставлен").count()
    matchs = Applications.objects.filter(status="Фабричный брак").count()
    matchs2 = Applications.objects.filter(status="Дорожный брак").count()
    product_ended = Products.objects.filter(count=0).count()

    return {
        "expectation": expectation,
        "confirmed": confirmed,
        "canceled": canceled,
        "transferred": transferred,
        "transferred_dispatcher": transferred_dispatcher,
        "drive": drive,
        "delivered": delivered,
        "matchs": matchs,
        "matchs2": matchs2,
        "product_ended": product_ended,
    }


def get_money():
    a = Applications.objects.all()
    confirmed_request = Applications.objects.filter(status="Подтвержден")
    dispatcher = Applications.objects.filter(status="Упакован")
    packer = Applications.objects.filter(status="Передан упаковщику")
    driver = Applications.objects.filter(status="В дороге")

    total = 0
    total_driver = 0
    total_packer = 0
    total_opt_price = 0
    total_confirmed = 0
    total_dispatcher = 0
    total_disp_pack_driv = 0
    total_sum_p = 0

    for i in Products.objects.all():
        total_sum_p += i.opt_price

    for dr in driver:
        try:
            total_disp_pack_driv += int(dr.price)
            total_driver += int(dr.price)
        except:
            pass

    for p in packer:
        try:
            total_disp_pack_driv += int(p.price)
            total_packer += int(p.price)
        except:
            pass

    for d in dispatcher:
        try:
            total_disp_pack_driv += int(d.price)
            total_dispatcher += int(d.price)
        except:
            pass

    for i in confirmed_request:
        try:
            total_confirmed += int(i.price)
        except:
            pass

    for i in a:
        try:
            if i.status == "Отменен" or i.status == "Фабричный брак" or i.status == "Дорожный брак":
                pass
            else:
                total_opt_price += int(i.opt_price)
                total += int(i.price)
        except:
            pass

    return {
        "1": round(total / 100 * 2.5, 10),
        "2": round(total, 10),
        "3": round(total_disp_pack_driv, 10),
        "4": round(total_dispatcher, 10),
        "5": round(total_packer, 10),
        "6": round(total_driver, 10),
        "7": total_sum_p,
        "8": (total_sum_p / 100) * 2.5,
        "9": Products.objects.all().count()
    }

@user_passes_test(lambda u: u.is_superuser)
def stats(request):
    return render(request, "django/contrib/admin/stats.html")

@user_passes_test(lambda u: u.is_superuser)
def stats2(request):
    return render(request, "admin/stats2.html", {
        "reports": get_report(),
        "money": get_money()
    })


urlpatterns = [
    path('admin/stats/', stats2, name="stats"),
    path('admin/', admin.site.urls),
    path('grappelli/', include('grappelli.urls')),  # grappelli URLS
    path('', include('aviato.urls'))
]
