from django import forms
from django.forms import ModelForm
from backend.moderation.models import Report


class ReportForm(ModelForm):
    description = forms.CharField(min_length=10)

    class Meta:
        model = Report
        fields = ("description",)
