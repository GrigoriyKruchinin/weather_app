import os

import requests
from django.urls import reverse
from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count

from .models import City, SearchHistory
from .forms import UserRegistrationForm


def register(request):
    """
    Регистрация нового пользователя.

    При успешной регистрации пользователя перенаправляет на главную
    страницу. Если запрос не POST, отображает форму регистрации.
    """
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
    """
    Главная страница приложения.

    Отображает историю поиска пользователя, количество поисков для
    каждого города, который пользователь проверял, и общее количество
    поисков для всех городов. Обрабатывает POST запрос для поиска погоды
    по городу.
    """
    error_message = request.GET.get("error_message", None)
    user_history = SearchHistory.objects.filter(user=request.user).order_by(
        "-search_datetime"
    )
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
            return redirect("weather", city_name=city_name)

    return render(
        request,
        "index.html",
        {
            "history": user_history,
            "user_city_counts": user_city_counts,
            "global_city_counts": global_city_counts,
            "error_message": error_message,
        },
    )


@login_required
def weather(request, city_name):
    """
    Получение и отображение погоды для указанного города.

    Если запрос к API успешен, отображает данные о погоде и сохраняет
    информацию о поиске в истории пользователя. В случае ошибки перенаправляет
    на главную страницу с сообщением об ошибке.
    """
    api_key = os.getenv("API_KEY")
    api_url = (
        f"http://api.openweathermap.org/data/2.5/weather?q={city_name}"
        f"&units=metric&appid={api_key}"
    )
    response = requests.get(api_url)

    if response.status_code == 200:
        weather_data = response.json()
        city, created = City.objects.get_or_create(name=city_name)
        SearchHistory.objects.create(user=request.user, city=city)
        return render(
            request, "weather.html", {"weather": weather_data, "city_name": city_name}
        )
    else:
        error_message = (
            f"Не удалось получить погоду для {city_name}. "
            "Возможно вы ввели несуществующий город."
        )
        return redirect(f"{reverse('index')}?error_message={error_message}")


@csrf_exempt
def city_search_count(request):
    """
    Получение количества поисков погоды для каждого города.

    Возвращает данные в формате JSON, где ключами являются имена
    городов, а значениями - количество поисков.
    """
    if request.method == "GET":
        city_counts = (
            SearchHistory.objects.values("city__name")
            .annotate(count=Count("city"))
            .order_by("-count")
        )
        data = {entry["city__name"]: entry["count"] for entry in city_counts}
        return JsonResponse(data, json_dumps_params={"ensure_ascii": False})


def city_autocomplete(request):
    """
    Возвращает список городов, соответствующих запросу.
    """
    if "term" in request.GET:
        term = request.GET["term"]
        cities = City.objects.filter(name__icontains=term).values_list(
            "name", flat=True
        )
        return JsonResponse(list(cities), safe=False)
    return JsonResponse([], safe=False)
