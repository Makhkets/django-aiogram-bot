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
                    "main_status": p.status,
                    "time_update_location": str(p.time_update_location).split(".")[0].split(":")[::1][0] + ":" + str(p.time_update_location).split(".")[0].split(":")[::1][-1],
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
                    "main_status": p.status,
                    "time_update_location": str(p.time_update_location).split(".")[0].split(":")[::1][0] + ":" + str(p.time_update_location).split(".")[0].split(":")[::1][-1],
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
            new_time_data = []
            for i in str(i.location_time).split("|"):
                new_time_data.append(str(i).split(".")[0].split(":")[::1][0] + ":" + str(i).split(".")[0].split(":")[::1][-1])
            data.append({
                "products": str(i.product),
                "address": str(i.address),
                "time_update_location": str(p.time_update_location).split(".")[0].split(":")[::1][0] + ":" + str(p.time_update_location).split(".")[0].split(":")[::1][-1],
                "time_locations": new_time_data,
                "price": str(i.price),
                "locations": str(i.location).split("|"),
                "last_location": str(i.location).split("|")[-1].split(".")[0].split(":")[::1][0] + ":" + str(i.location).split("|")[-1].split(".")[0].split(":")[::1][-1],
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