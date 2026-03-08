from django import forms
from django.forms import ModelForm
from backend.moderation.models import ModerationAction, Report


class ReportForm(ModelForm):
    description = forms.CharField(required=False)

    class Meta:
        model = Report
        fields = ("description",)


class ModerationActionForm(ModelForm):
    note = forms.CharField(required=False)

    class Meta:
        model = ModerationAction
        fields = ("note",)
