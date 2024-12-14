from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
	username = models.CharField(
		max_length=150,
		unique=True,
		help_text="Введите ваше имя пользователя. Допустимо до 150 символов. Только буквы, цифры, и @/./+/-/_",
	)

	password = models.CharField(
		max_length=128,
		verbose_name="password",
		help_text="Введите пароль. Пароль будет сохранен в зашифрованном виде."
	)