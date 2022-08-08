from django.urls import path
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse

from .forms import Geo
from .models import Applications

from loguru import logger


class MyJsonResponse(JsonResponse):
    def __init__(self, data, encoder=DjangoJSONEncoder, safe=True, **kwargs):
        json_dumps_params = dict(ensure_ascii=False)
        super().__init__(data, encoder, safe, json_dumps_params, **kwargs)


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
                r = MyJsonResponse({
                    "products": p.product,
                    "address": p.address,
                    "status": "Ваш товар в дороге!",
                    "time_update_location": p.time_update_location,
                    "price": p.price,
                    "location": p.location,
                    "phone": p.phone,
                    "id": p.pk,
                }, safe=False)
                r["Access-Control-Allow-Origin"] = "*"
                return r
            else:
                r = MyJsonResponse({
                    "products": p.product,
                    "address": p.address,
                    "status": "Ваш товар подготавливается к отправке!",
                    "time_update_location": p.time_update_location,
                    "price": p.price,
                    "location": p.location,
                    "phone": p.phone,
                    "id": p.pk,
                }, safe=False)
                r["Access-Control-Allow-Origin"] = "*"
                return r                


    except Exception as ex:
        logger.error(ex)

    p = Applications.objects.filter(phone=id_or_phone)

    if len(p) >= 1:
        data = []
        for i in p:
            data.append({
                "products": str(i.product),
                "address": str(i.address),
                "last_time_update_location": str(i.time_update_location),
                "time_locations": str(i.location_time).split("|"),
                "price": str(i.price),
                "locations": str(i.location).split("|"),
                "last_location": str(i.location).split("|")[-1],
                "phone": str(i.phone),
                "id": str(i.pk),
            })

        r = MyJsonResponse(data, safe=False)
        r["Access-Control-Allow-Origin"] = "*"
        return r

    return MyJsonResponse({
        "message": "Error, product not finded"
    })

urlpatterns = [
    path('', index),
    path('data/<str:id>', data),
]