from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class UserRegistrationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["username"].label = "Логин"
        self.fields["password1"].label = "Пароль"
        self.fields["password2"].label = "Подтверждение пароля"

        self.fields["username"].help_text = None
        self.fields["password1"].help_text = None
        self.fields["password2"].help_text = None

    class Meta:
        model = User
        fields = ["username", "password1", "password2"]
