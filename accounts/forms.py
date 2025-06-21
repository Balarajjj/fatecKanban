from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="E-mail institucional",
        widget=forms.EmailInput(
            attrs={
                "class": "w-full border border-gray-300 rounded-md px-3 py-2 mt-1 focus:outline-none focus:ring-2 focus:ring-fatecRed",
                "placeholder": "seunome@fatec.sp.gov.br",
                "autocomplete": "username",
            }
        ),
    )
    password = forms.CharField(
        label="Senha",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "w-full border border-gray-300 rounded-md px-3 py-2 mt-1 focus:outline-none focus:ring-2 focus:ring-fatecRed",
                "placeholder": "Sua senha",
                "autocomplete": "current-password",
            }
        ),
    )


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        label="E-mail institucional",
        widget=forms.EmailInput(
            attrs={
                "class": "w-full border border-gray-300 rounded-md px-3 py-2 mt-1 focus:outline-none focus:ring-2 focus:ring-fatecRed",
                "placeholder": "seunome@fatec.sp.gov.br",
                "autocomplete": "email",
            }
        ),
    )

    class Meta:
        model = User
        fields = ("username", "email")  # campos usados no form
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "w-full border border-gray-300 rounded-md px-3 py-2 mt-1 focus:outline-none focus:ring-2 focus:ring-fatecRed",
                    "placeholder": "Nome de usuário",
                    "autocomplete": "username",
                }
            ),
        }
