from django.urls import path
from frontend.views.matchups.views import HomeView
from frontend.views.competitors.views import CompetitorView
from frontend.views.ratings.views import RatingView
from frontend.views.profiles.views import ProfileView, RegisterView, LoginView
from django.contrib.auth import views as auth_views

urlpatterns = [
	path('', HomeView.as_view(), name='home'),  # Пример маршрута
	path('competitor/<int:competitor_id>', CompetitorView.as_view(), name='competitor'),
	path('rating/', RatingView.as_view(), name='rating'),
	path('profile/', ProfileView.as_view(), name='profile'),
	path('register/', RegisterView.as_view(), name='register'),
	path('login/', LoginView.as_view(), name='login'),
	path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
]