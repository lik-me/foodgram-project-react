from django.contrib.auth.models import AbstractUser
from django.db import models

USER = "user"
ADMIN = "admin"

ROLE_CHOICES = [(USER, USER), (ADMIN, ADMIN)]


class User(AbstractUser):

    username = models.CharField(
        "Username",
        max_length=150,
        unique=True,
        null=False,)
    first_name = models.CharField(
        "Имя",
        max_length=150,
        null=False,
    )
    last_name = models.CharField(
        "Фамилия",
        max_length=150,
        null=False,
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        null=False,
    )
    role = models.CharField(
        "Роль",
        max_length=10,
        choices=ROLE_CHOICES,
        default=USER,
        blank=True,
    )
    password = models.CharField(
        max_length=150,
        null=False,
    )

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_admin(self):
        return self.role == ADMIN

    class Meta:
        ordering = ("username",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username
