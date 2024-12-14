from django import forms
from .models import User

class RegistrationForm(forms.ModelForm):
	username = forms.CharField(
		max_length=150,
		help_text="Введите ваше имя пользователя. До 150 символов.",
		widget=forms.TextInput(attrs={
			'placeholder': 'Введите имя пользователя',
		})
	)
	password = forms.CharField(
		widget= forms.PasswordInput(attrs={
			'placeholder': 'Введите пароль',
		})
	)
	confirm_password = forms.CharField(

		label= "Подтвердите пароль",
		widget= forms.PasswordInput(attrs={
			'placeholder': 'Подтвердите пароль',
		})
	)

	class Meta:
		model = User
		fields = ['username', 'password']


	def clean_username(self):
		username = self.cleaned_data.get('username')
		if User.objects.filter(username=username).exists():
			raise forms.ValidationError("Имя пользователя уже занято. Выберите другое.")
		return username

	def clean_password(self):
		password = self.cleaned_data.get('password')
		if len(password) < 4:
			raise forms.ValidationError("Пароль должен содержать минимум 4 символа.")
		return password

	def clean(self):
		cleaned_data = super().clean()
		password = cleaned_data.get("password")
		confirm_password = cleaned_data.get("confirm_password")

		if password != confirm_password:
			# Привязываем ошибку к полю confirm_password
			self.add_error('confirm_password', "Пароли не совпадают.")
		return cleaned_data