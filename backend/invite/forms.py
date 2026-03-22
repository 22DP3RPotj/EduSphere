from datetime import datetime
from typing import Optional
from django import forms
from django.forms import ModelForm
from django.utils import timezone
from backend.invite.models import Invite


class InviteForm(ModelForm):
    class Meta:
        model = Invite
        fields = ("expires_at",)

    def clean_expires_at(self) -> Optional[datetime]:
        expires_at = self.cleaned_data.get("expires_at")

        if expires_at and expires_at <= timezone.now():
            raise forms.ValidationError("Expiration time must be in the future.")

        return expires_at
