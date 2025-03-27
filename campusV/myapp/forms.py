from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario

class RegistroUsuarioForm(UserCreationForm):
    tipo = forms.ChoiceField(choices=[('alumno', 'Alumno'), ('maestro', 'Maestro')], label="Tipo de usuario")

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password1', 'password2', 'tipo']
