from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from .models import User, Room, Message, Report, Invite, Role

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'name', 'email', 'password1', 'password2']


class RoomForm(ModelForm):
    name = forms.CharField(
        max_length=64, 
        validators=[
            RegexValidator(
                regex='^[a-zA-Z0-9 ]+$',
                message="Room name can only contain letters and numbers.",
                code='invalid_room_name'
            )
        ]
    )
    
    description = forms.CharField(widget=forms.Textarea, required=False)
        
    class Meta:
        model = Room
        fields = ('name', 'description', 'default_role', 'visibility')
        
    def clean_name(self) -> str:
        name = self.cleaned_data['name']
        return ' '.join(name.strip().split())


class UserForm(ModelForm):
    avatar = forms.ImageField(widget=forms.FileInput, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'name', 'avatar', 'bio')


class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = ('body',)


class ReportForm(ModelForm):
    class Meta:
        model = Report
        fields = ('reason', 'body')


class InviteForm(ModelForm):
    class Meta:
        model = Invite
        fields = ('expires_at')


class RoleForm(ModelForm):
    class Meta:
        model = Role
        fields = ('name', 'description', 'priority')
