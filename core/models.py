from django.db import models
from django.contrib.auth.models import User


class City(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class SearchHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    search_datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-search_datetime"]
