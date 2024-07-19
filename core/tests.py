from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch

from .models import City, SearchHistory


# Тест для отладки
class SimpleTest(TestCase):
    def test_addition(self):
        n = 2 + 2
        self.assertEqual(n, 4)


# Тесты для представлений
class ViewTests(TestCase):
    def setUp(self):
        # Создаем тестового пользователя
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.login(username="testuser", password="testpassword")

    def test_register_view_get(self):
        # Проверяем GET запрос к представлению регистрации
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register.html")

    def test_register_view_post(self):
        # Проверяем POST запрос к представлению регистрации с валидными данными
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "password1": "newpassword",
                "password2": "newpassword",
            },
        )
        self.assertEqual(response.status_code, 302)  # Ожидаем редирект
        self.assertRedirects(response, reverse("index"))
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_index_view(self):
        # Проверяем GET запрос к главной странице
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")

    @patch("requests.get")
    def test_weather_view_success(self, mock_get):
        # Проверяем успешный запрос погоды
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {"weather": "sunny"}
        City.objects.create(name="TestCity")

        response = self.client.get(reverse("weather", args=["TestCity"]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "weather.html")
        self.assertContains(response, "TestCity")

    def test_weather_view_failure(self):
        # Проверяем запрос погоды с ошибкой
        with patch("requests.get") as mock_get:
            mock_get.return_value.status_code = 404
            response = self.client.get(reverse("weather", args=["UnknownCity"]))
            self.assertEqual(response.status_code, 302)
            self.assertRedirects(
                response,
                f"{reverse('index')}?error_message=Не удалось получить погоду для UnknownCity. Возможно вы ввели несуществующий город.",
            )

    def test_city_search_count_view(self):
        # Проверяем запрос на количество поисков по городам
        City.objects.create(name="TestCity")
        SearchHistory.objects.create(
            user=self.user, city=City.objects.get(name="TestCity")
        )

        response = self.client.get(reverse("city_search_count"))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"TestCity": 1})
