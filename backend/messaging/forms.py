from django import forms
from django.forms import ModelForm
from backend.messaging.models import Message


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
