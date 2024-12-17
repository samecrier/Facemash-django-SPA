from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
from apps.profiles.forms import RegistrationForm
from service.profiles.data_service import ProfileGetData
from django.core.paginator import Paginator


class ProfileView(View):

	data_helper_service = ProfileGetData()

	def get(self, request):
		data = self.data_helper_service.get_n_profile_matchups(request.user, 100)
		data = sorted(data.items())
		paginator = Paginator(data, 20)
		page_number = request.GET.get('page', 1)
		page_obj = paginator.get_page(page_number)
		return render(request, 'frontend/profile.html', {'page_obj': page_obj})

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

	def get_success_url(self):
		next_url = self.request.GET.get('next')
		if next_url:
			return next_url
		return self.get_redirect_url() or settings.LOGIN_REDIRECT_URL
	
	def form_invalid(self, form):
		form.errors.clear()
		# Добавляем кастомное сообщение об ошибке
		form.add_error(None, "Неверное имя пользователя или пароль. Попробуйте снова.")
		return self.render_to_response(self.get_context_data(form=form))