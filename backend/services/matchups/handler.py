from django.db import transaction
from services.competitors.service import LocalCompetitorService
from services.matchups.service import LocalMatchupService
from services.ratings.service import LocalRatingService
from services.profiles.service import LocalProfileService
from services.ratings.rating_systems import EloRatingSystem32, EloRatingSystem64

class MatchupHandler():

	def __init__(self, request, winner_id, loser_id, 
				rating_system=EloRatingSystem64(), 
				tournament_matchup_id=None):
		self.competitor_service = LocalCompetitorService()
		self.matchup_service = LocalMatchupService()
		self.rating_service = LocalRatingService()
		self.profile_service = LocalProfileService()
		self.rating_system = rating_system
		self.tournament_matchup_id = tournament_matchup_id
		
		self.request = request
		self.winner_id = winner_id
		self.losers = loser_id

		self.delta_winner = 0
		self.delta_loser = 0
		self.delta_winner_profile = 0
		self.delta_loser_profile = 0
	
	@transaction.atomic
	def process_matchup(self) -> None:
		"""
		Процесс расчета рейтингов и создания Matchup
		"""

		winner = self.competitor_service.get_competitor_object(self.winner_id)
		if self.request.user.is_authenticated:
			profile_id = self.request.user
		else:
			profile_id = self.profile_service.get_guest_profile()
		curr_winner_rating = self.rating_service.get_rating(winner)
		curr_winner_rating_profile = self.rating_service.get_rating_profile(profile_id, winner)
		
		if isinstance(self.losers, (int, str)):
			loser = self.losers
			self.solo_matchup(winner, loser, curr_winner_rating, curr_winner_rating_profile)
		elif isinstance(self.losers, list):
			for loser in self.losers:
				self.solo_matchup(winner, loser, curr_winner_rating, curr_winner_rating_profile)
	
	def solo_matchup(self, winner, loser, curr_winner_rating, curr_winner_rating_profile):
		
		loser = self.competitor_service.get_competitor_object(loser)
		curr_loser_rating = self.rating_service.get_rating(loser)

		delta = self.rating_system.delta(curr_winner_rating, curr_loser_rating)
		delta_winner = delta
		delta_loser = -delta

		self.delta_winner += delta_winner
		self.delta_loser += delta_loser

		if self.request.user.is_authenticated:
			profile_id = self.request.user
		else:
			profile_id = self.profile_service.get_guest_profile()
		

		curr_loser_rating_profile = self.rating_service.get_rating_profile(profile_id, loser)
		
		delta_profile = self.rating_system.delta(curr_winner_rating_profile, curr_loser_rating_profile)
		delta_winner_profile = delta_profile
		delta_loser_profile = -delta_profile

		self.delta_winner_profile += delta_winner_profile
		self.delta_loser_profile += delta_loser_profile


		self.matchup_service.create_matchup(
				winner_id=winner,
				loser_id=loser,
				delta_winner=delta_winner,
				delta_loser=delta_loser,
				delta_winner_profile=delta_winner_profile,
				delta_loser_profile=delta_loser_profile,
				rating_system=self.rating_system,
				profile_id=profile_id,
				tournament_matchup_id=self.tournament_matchup_id
		)
		
		self.rating_service.update_matchup_rating(winner, delta_winner, 1)
		self.rating_service.update_matchup_rating(loser, delta_loser, 0)

		self.rating_service.update_matchup_ratingprofile(profile_id, winner, delta_winner_profile, 1)
		self.rating_service.update_matchup_ratingprofile(profile_id, loser, delta_loser_profile, 0)
