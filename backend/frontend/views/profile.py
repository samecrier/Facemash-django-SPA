from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.views import View
from profiles.forms import RegistrationForm
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm


class ProfileView(View):

	def get(self, request):
		return render(request, 'frontend/profile.html')

class RegisterView(FormView):
	template_name = 'frontend/register.html'
	form_class = RegistrationForm
	success_url = reverse_lazy('home')

	def form_valid(self, form):
		# Создаем пользователя
		user = form.save(commit=False)
		user.set_password(form.cleaned_data['password'])
		user.save()
		# Вход пользователя в систему
		login(self.request, user)
		# Редирект на success_url
		return redirect(self.success_url)

	def form_invalid(self, form):
		# Отображение ошибок, если форма не валидна
		return self.render_to_response(self.get_context_data(form=form))
	
class LoginView(LoginView):
	template_name = 'frontend/login.html'
	authentication_form = AuthenticationForm
	success_url = reverse_lazy('profile')

	def get_success_url(self):
		# Используем success_url для перенаправления после успешного входа
		return self.success_url

	def form_invalid(self, form):
		form.errors.clear()
		# Добавляем кастомное сообщение об ошибке
		form.add_error(None, "Неверное имя пользователя или пароль. Попробуйте снова.")
		return self.render_to_response(self.get_context_data(form=form))