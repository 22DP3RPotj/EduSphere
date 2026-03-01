from backend.access.models import Role
from django.forms import ModelForm


class RoleForm(ModelForm):
    class Meta:
        model = Role
        fields = ("name", "description", "priority")
