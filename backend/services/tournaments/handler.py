from django.db import transaction
from services.competitors.service import LocalCompetitorService
from services.matchups.service import LocalMatchupService
from services.ratings.service import LocalRatingService
from services.profiles.service import LocalProfileService
from services.tournaments.service import LocalTournamentService
from services.tournaments.helper import TournamentHelper

class TournamentHandler():
	
	def __init__(
			self,
			competitor_service = LocalCompetitorService(),
			matchup_service = LocalMatchupService(),
			rating_service = LocalRatingService(),
			profile_service = LocalProfileService(),
			tournament_service = LocalTournamentService(),
			tournament_helper = TournamentHelper()
	):
		self.competitor_service = competitor_service
		self.matchup_service = matchup_service
		self.rating_service = rating_service
		self.profile_service = profile_service
		self.tournament_service = tournament_service
		self.tournament_helper = tournament_helper

	@transaction.atomic
	def process_tournament(self, request, cities, participants, rounds, in_matchup):
		round_obj = None
		if request.user.is_authenticated:
			profile_id = request.user
			competitors = self.competitor_service.fetch_competitors_by_location(cities)
			competitor_for_tournament = self.tournament_helper.choose_random_competitors(competitors, participants)
			round_obj = self.initiate_of_tournament(profile_id, competitor_for_tournament, participants, rounds, in_matchup)
		
	
	def initiate_of_tournament(self, profile_id, competitors, participants, rounds, in_matchup):
		tournament_obj = self.tournament_service.create_tournament_base(
			profile_id=profile_id,
			competitors_number=participants,
			rounds_number=rounds
		)
		round_obj = self.tournament_service.create_tournament_round(
			tournament_base_id=tournament_obj,
			competitors_in_matchup=in_matchup
		)
		for competitor in competitors:
			tournament_competitor_obj = self.tournament_service.create_tournament_competitor(
				tournament_base_id=tournament_obj,
				competitor_id=competitor,
			)
			self.tournament_service.create_round_competitor(
				tournament_competitor_id=tournament_competitor_obj,
				tournament_round_id=round_obj,
			)
		return round_obj
