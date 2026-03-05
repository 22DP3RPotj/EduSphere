import datetime
from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from django.utils import timezone
from django.utils.text import slugify
from backend.account.models import User
from backend.messaging.models import Message
from backend.invite.models import Invite
from backend.moderation.models import Report
from backend.room.models import Room


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "name", "email", "password1", "password2")


class RoomForm(ModelForm):
    name = forms.CharField(
        max_length=64,
        validators=[
            RegexValidator(
                regex="^[a-zA-Z0-9 ]+$",
                message="Room name can only contain letters and numbers.",
                code="invalid_room_name",
            )
        ],
    )

    description = forms.CharField(required=False)

    class Meta:
        model = Room
        fields = ("name", "description")

    def clean_name(self) -> str:
        name = self.cleaned_data["name"]
        return " ".join(name.strip().split())


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


class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = ("body",)

    def clean_body(self) -> str:
        body = self.cleaned_data.get("body", "")

        trimmed = body.strip()

        if not trimmed:
            raise forms.ValidationError("Message cannot be empty.")

        return trimmed


class ReportForm(ModelForm):
    class Meta:
        model = Report
        fields = ("body",)


class InviteForm(ModelForm):
    class Meta:
        model = Invite
        fields = ("expires_at",)

    def clean_expires_at(self) -> datetime.datetime | None:
        expires_at = self.cleaned_data.get("expires_at")

        if expires_at and expires_at <= timezone.now():
            raise forms.ValidationError("Expiration time must be in the future.")

        return expires_at
