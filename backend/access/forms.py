from django.forms import ModelForm

from backend.access.models import Role


class RoleForm(ModelForm):
    class Meta:
        model = Role
        fields = ("name", "description", "priority")
