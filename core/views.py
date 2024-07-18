import os
import requests

from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count

from .models import City, SearchHistory
from .forms import UserRegistrationForm


def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect("index")
    else:
        form = UserRegistrationForm()
    return render(request, "register.html", {"form": form})


@login_required
def index(request):
    if request.method == "POST":
        city_name = request.POST.get("city_name")
        if city_name:
            city, created = City.objects.get_or_create(name=city_name)
            SearchHistory.objects.create(user=request.user, city=city)
            return redirect("weather", city_name=city_name)

    history = SearchHistory.objects.filter(user=request.user).order_by(
        "-search_datetime"
    )
    city_counts = (
        SearchHistory.objects.values("city__name")
        .annotate(count=Count("city__name"))
        .order_by("-count")
    )
    return render(
        request, "index.html", {"history": history, "city_counts": city_counts}
    )


@login_required
def weather(request, city_name):
    api_key = os.getenv("API_KEY")
    api_url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&units=metric&appid={api_key}"
    response = requests.get(api_url)

    if response.status_code == 200:
        weather_data = response.json()
        return render(
            request, "weather.html", {"weather": weather_data, "city_name": city_name}
        )
    else:
        error_message = (
            f"Не удалось получить погоду для {city_name}. Попробуйте еще раз."
        )
        return render(request, "index.html", {"error_message": error_message})


@csrf_exempt
def city_search_count(request):
    if request.method == "GET":
        city_counts = (
            SearchHistory.objects.values("city_name")
            .annotate(count=Count("city_name"))
            .order_by("-count")
        )
        data = {entry["city_name"]: entry["count"] for entry in city_counts}
        return JsonResponse(data)
