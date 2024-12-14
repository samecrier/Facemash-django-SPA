from django.urls import path
from .views import matchup, profile, competitor
from django.contrib.auth import views as auth_views

urlpatterns = [
	path('', matchup.HomeViewJS.as_view(), name='home'),  # Пример маршрута
	path('competitor/<int:competitor_id>', competitor.CompetitorView.as_view(), name='competitor'),
	path('profile/', profile.ProfileView.as_view(), name='profile'),
	path('register/', profile.RegisterView.as_view(), name='register'),
	path('login/', profile.LoginView.as_view(), name='login'),
	path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
	path('register/', profile.RegisterView.as_view(), name='register'),
]