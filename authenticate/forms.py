from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.models import User
from django import forms


class SignUpForm(UserCreationForm):
    username = forms.CharField(label="Usuário",max_length=32, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    first_name = forms.CharField(label="Nome", max_length=32, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(label="Sobrenome", max_length=32, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    email = forms.EmailField(label="Email", max_length=50, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    password1 = forms.CharField(label="Senha", max_length=40, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    password2 = forms.CharField(label="Confirmação senha", max_length=40, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']


class EditProfileForm(UserChangeForm):
    username = forms.CharField(label="Usuário:", max_length=32, widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(label="Nome:", max_length=32, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label="Sobrenome:", max_length=32, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Email", max_length=50, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = None
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(label="Senha antiga:", max_length=40, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password1 = forms.CharField(label="Senha nova:", max_length=40, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = forms.CharField(label="Confirmação senha nova:", max_length=40, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    class Meta:
        model = User
