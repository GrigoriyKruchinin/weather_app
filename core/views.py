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
    error_message = None
    user_history = SearchHistory.objects.filter(user=request.user).order_by("-search_datetime")
    user_city_counts = (
        user_history.values("city__name")
        .annotate(count=Count("city"))
        .order_by("-count")
    )
    global_city_counts = (
        SearchHistory.objects.values("city__name")
        .annotate(count=Count("city"))
        .order_by("-count")
    )

    if request.method == "POST":
        city_name = request.POST.get("city_name")
        if city_name:
            api_key = os.getenv("API_KEY")
            api_url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&units=metric&appid={api_key}"
            response = requests.get(api_url)
            if response.status_code == 200:
                return redirect("weather", city_name=city_name)
            else:
                error_message = "Введите существующий город."

    return render(
        request,
        "index.html",
        {
            "history": user_history,
            "user_city_counts": user_city_counts,
            "global_city_counts": global_city_counts,
            "error_message": error_message,
        }
    )

@login_required
def weather(request, city_name):
    api_key = os.getenv("API_KEY")
    api_url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&units=metric&appid={api_key}"
    response = requests.get(api_url)
    if response.status_code == 200:
        weather_data = response.json()
        city, created = City.objects.get_or_create(name=city_name)
        SearchHistory.objects.create(user=request.user, city=city)
        return render(
            request, "weather.html", {"weather": weather_data, "city_name": city_name}
        )
    else:
        error_message = f"Не удалось получить погоду для {city_name}. Попробуйте еще раз."
        return render(request, "index.html", {"error_message": error_message})

@csrf_exempt
def city_search_count(request):
    if request.method == "GET":
        city_counts = (
            SearchHistory.objects
            .values("city__name")
            .annotate(count=Count("city"))
            .order_by("-count")
        )
        data = {entry["city__name"]: entry["count"] for entry in city_counts}
        return JsonResponse(data, json_dumps_params={'ensure_ascii': False})
