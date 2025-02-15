from django import forms
from django.forms import ModelForm
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from .models import User, Room


class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            'placeholder': 'johndoe@gmail.com',
            'autocomplete': 'email'
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'placeholder': '••••••••',
            'autocomplete': 'current-password'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if user is None:
                raise forms.ValidationError("Invalid email or password")
        return cleaned_data

class RegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'placeholder': 'johndoe',
            'autocomplete': 'username'
        })
        self.fields['name'].widget.attrs.update({
            'placeholder': 'John Doe',
            'autocomplete': 'name'
        })
        self.fields['email'].widget.attrs.update({
            'placeholder': 'johndoe@gmail.com',
            'autocomplete': 'email'
        })
        self.fields['password1'].widget.attrs.update({
            'placeholder': '••••••••',
            'autocomplete': 'new-password'
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': '••••••••',
            'autocomplete': 'new-password'
        })

    class Meta:
        model = User
        fields = ['username', 'name', 'email', 'password1', 'password2']

class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'participants', 'slug']

class UserForm(ModelForm):
    avatar = forms.ImageField(widget=forms.FileInput)
    class Meta:
        model = User
        fields = ['username', 'name', 'email', 'avatar', 'bio']
        