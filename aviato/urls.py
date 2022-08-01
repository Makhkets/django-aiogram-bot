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
        logger.critical(p)
        if p:
            return JsonResponse({
                "products": p.product,
                "note": p.note,
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
                "note": str(i.note),
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