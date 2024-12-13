from django.urls import path
from . import views

urlpatterns = [
	path('archieve', views.HomeView.as_view(), name='home-archieve'),  # Пример маршрута
	path('', views.HomeViewJS.as_view(), name='home'),  # Пример маршрута
	path('profile/<int:profile_id>', views.ProfileView.as_view(), name='profile'),
]