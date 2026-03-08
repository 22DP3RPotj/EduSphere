from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.utils.text import slugify
from backend.account.models import User


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "name", "email", "password1", "password2")


class UserForm(ModelForm):
    avatar = forms.ImageField(widget=forms.FileInput, required=False)

    username = forms.SlugField(
        error_messages={
            "invalid": "Username can only contain letters, numbers, underscores, and hyphens."
        }
    )

    class Meta:
        model = User
        fields = ("username", "name", "avatar", "bio")

    def clean_username(self) -> str:
        username = self.cleaned_data["username"]
        return slugify(username.strip())
