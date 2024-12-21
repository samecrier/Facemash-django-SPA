from django.urls import path
from frontend.views.matchups.views import MatchupView
from frontend.views.competitors.views import CompetitorView
from frontend.views.ratings.views import RatingView
from frontend.views.tournaments.views import TournamentView, WinnerTournamentView, StageTournamentView, ConfirmationCreateTournamentView, HomeTournamentView, CreateTournamentView, MatchupTournamentView
from frontend.views.profiles.views import ProfileView, RegisterView, LoginView
from django.contrib.auth import views as auth_views

urlpatterns = [
	path('', MatchupView.as_view(), name='home'),  # Пример маршрута
	
	path('tournament/', HomeTournamentView.as_view(), name='tournament-home'),
	path('tournament/<int:tournament_id>/<int:round_number>/0', MatchupTournamentView.as_view(), name='tournament-matchup-actual'),
	path('tournament/<int:tournament_id>/<int:round_number>/<int:matchup_number>', MatchupTournamentView.as_view(), name='tournament-matchup'),
	path('tournament/<int:tournament_id>/<int:round_number>', StageTournamentView.as_view(), name='tournament-stage'),
	path('tournament/<int:tournament_id>', TournamentView.as_view(), name='tournament-info'),
	path('tournament/<int:tournament_id>/confirmation', ConfirmationCreateTournamentView.as_view(), name='tournament-confirmation'),
	path('tournament/<int:tournament_id>/winner', WinnerTournamentView.as_view(), name='tournament-winner'),
	path('tournament/create', CreateTournamentView.as_view(), name='tournament-create'),
	path('competitor/<int:competitor_id>', CompetitorView.as_view(), name='competitor'),
	path('rating/', RatingView.as_view(), name='rating'),
	path('profile/', ProfileView.as_view(), name='profile'),
	path('register/', RegisterView.as_view(), name='register'),
	path('login/', LoginView.as_view(), name='login'),
	path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
]