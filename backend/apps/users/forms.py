from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import User


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = User
        fields = (
            'username', 'first_name',
            'last_name', 'role', 'email', 'is_staff')


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = User
        fields = (
            'username', 'first_name',
            'last_name', 'role', 'email', 'is_staff',)
