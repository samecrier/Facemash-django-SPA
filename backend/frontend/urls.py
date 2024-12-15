from django.urls import path
from .views import view_competitor, view_matchup, view_profile, view_rating, api_competitor
from django.contrib.auth import views as auth_views

urlpatterns = [
	path('', view_matchup.HomeView.as_view(), name='home'),  # Пример маршрута
	path('competitor/<int:competitor_id>', view_competitor.CompetitorView.as_view(), name='competitor'),
	path('rating/', view_rating.RatingView.as_view(), name='rating'),
	path('profile/', view_profile.ProfileView.as_view(), name='profile'),
	path('register/', view_profile.RegisterView.as_view(), name='register'),
	path('login/', view_profile.LoginView.as_view(), name='login'),
	path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
	path('register/', view_profile.RegisterView.as_view(), name='register'),
	path('api/v01/competitor/<int:competitor_id>/', api_competitor.get_competitor, name='api-competitor'),
]