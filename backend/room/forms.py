from django import forms
from django.forms import ModelForm
from django.core.validators import RegexValidator
from backend.room.models import Room


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
