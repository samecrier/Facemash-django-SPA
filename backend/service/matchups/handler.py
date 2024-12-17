from django.db import transaction
from service.competitors.service import LocalCompetitorService
from service.matchups.service import LocalMatchupService
from service.ratings.service import LocalRatingService
from service.profiles.service import LocalProfileService
from service.ratings.ratings_system import EloRatingSystem32, EloRatingSystem64

class MatchupHandler():

	def __init__(self, request, winner_id, loser_id):
		self.competitor_service = LocalCompetitorService()
		self.matchup_service = LocalMatchupService()
		self.rating_service = LocalRatingService()
		self.profile_service = LocalProfileService()
		self.rating_system = EloRatingSystem64()
		
		self.request = request
		self.winner = self.competitor_service.get_competitor_object(winner_id)
		self.loser = self.competitor_service.get_competitor_object(loser_id)
	
	@transaction.atomic
	def process_matchup(self) -> None:
		curr_winner_rating = self.rating_service.get_rating(self.winner)
		curr_loser_rating = self.rating_service.get_rating(self.loser)

		delta = self.rating_system.delta(curr_winner_rating, curr_loser_rating)
		delta_winner = delta
		delta_loser = -delta

		if self.request.user.is_authenticated:
			profile_id = self.request.user
		else:
			profile_id = self.profile_service.get_guest_profile()

		curr_winner_rating_profile = self.rating_service.get_rating_profile(profile_id, self.winner)
		curr_loser_rating_profile = self.rating_service.get_rating_profile(profile_id, self.loser)
		
		delta_profile = self.rating_system.delta(curr_winner_rating_profile, curr_loser_rating_profile)
		delta_winner_profile = delta_profile
		delta_loser_profile = -delta_profile

		self.matchup_service.create_matchup(
				winner_id=self.winner, 
				loser_id=self.loser,
				delta_winner=delta_winner, 
				delta_loser=delta_loser,
				delta_winner_profile=delta_winner_profile,
				delta_loser_profile=delta_loser_profile,
				rating_system=self.rating_system,
				profile_id=profile_id
		)
		self.rating_service.update_matchup_rating(self.winner, delta_winner, 1)
		self.rating_service.update_matchup_rating(self.loser, delta_loser, 0)

		self.rating_service.update_matchup_ratingprofile(profile_id, self.winner, delta_winner_profile, 1)
		self.rating_service.update_matchup_ratingprofile(profile_id, self.loser, delta_loser_profile, 0)
