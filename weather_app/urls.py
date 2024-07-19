from django.urls import path
from django.contrib.auth import views as auth_views
from core import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path(
        "login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(template_name="logout.html"),
        name="logout",
    ),
    path("", views.index, name="index"),
    path("weather/<str:city_name>/", views.weather, name="weather"),
    path("api/city_search_count/", views.city_search_count, name="city_search_count"),
    path('city-autocomplete/', views.city_autocomplete, name='city_autocomplete'),

]
