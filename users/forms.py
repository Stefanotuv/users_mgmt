from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User,Profile
from allauth.account.forms import LoginForm

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('email',)

class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = ('email',)



class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        # fields = ['name','email', 'password1', 'password2'] # old version
        fields = ['email', 'password1', 'password2']

class UserUpdateForm(forms.ModelForm):
    # email = forms.EmailField()

    class Meta:
        model = User
        fields = ['name','email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['address','image']

class UserLoginForm(LoginForm):
    email = forms.EmailField(),

    class Meta:
        model = User
        fields = ['email', 'password']




