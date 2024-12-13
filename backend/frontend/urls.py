from django.urls import path
from . import views

urlpatterns = [
	path('', views.HomeView.as_view(), name='home'),  # Пример маршрута
	path('js', views.HomeViewJS.as_view(), name='home_js'),  # Пример маршрута
]