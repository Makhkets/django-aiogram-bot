from django.urls import path
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from .forms import Geo
from loguru import logger
from .models import Applications

def index(request):
    if request.method == "POST":
        id_or_phone = request.POST.get("id_or_phone")

        try:
            p = Applications.objects.filter(pk=id_or_phone)
            logger.success(p)
            if len(p) >= 1:
                return render(request, "index.html", {
                    "form": Geo(),
                    "products": p
                })
        except: pass

        p = Applications.objects.filter(phone=id_or_phone)
        logger.success(p)

        if len(p) >= 1:
            return render(request, "index.html", {
                "form": Geo(),
                "products": p
            })

        return render(request, "index.html", {
            "form": Geo(),
            "message": "Ничего не найдено"
        })

    return render(request, "index.html", {
        "form": Geo(),
    })

def data(request, id):
    id_or_phone = id
    try:
        p = Applications.objects.get(pk=id_or_phone)
        if p:
            if p.status == "В дороге":
                return JsonResponse({
                    "products": p.product,
                    "address": p.address,
                    "status": "Ваш товар в дороге!",
                    "time_update_location": p.time_update_location,
                    "price": p.price,
                    "location": p.location,
                    "phone": p.phone,
                    "id": p.pk,
                }, safe=False)
            else:
                return JsonResponse({
                    "products": p.product,
                    "address": p.address,
                    "status": "Ваш товар подготавливается к отправке!",
                    "time_update_location": p.time_update_location,
                    "price": p.price,
                    "location": p.location,
                    "phone": p.phone,
                    "id": p.pk,
                }, safe=False)                


    except Exception as ex:
        logger.error(ex)

    p = Applications.objects.filter(phone=id_or_phone)

    if len(p) >= 1:
        data = []
        for i in p:
            data.append({
                "products": str(i.product),
                "address": str(i.address),
                "time_update_location": str(i.time_update_location),
                "price": str(i.price),
                "location": str(i.location),
                "phone": str(i.phone),
                "id": str(i.pk),
            })

        return JsonResponse(data, safe=False)

    return JsonResponse({
        "message": "Error, product not finded"
    })

urlpatterns = [
    path('', index),
    path('data/<str:id>', data),
]