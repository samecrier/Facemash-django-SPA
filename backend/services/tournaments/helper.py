from services.competitors.service import LocalCompetitorService
from services.matchups.service import LocalMatchupService
from services.ratings.service import LocalRatingService
from services.profiles.service import LocalProfileService
from services.tournaments.service import LocalTournamentService
import random

class TournamentHelper():

	def __init__(
			self,
			competitor_service = LocalCompetitorService(),
			matchup_service = LocalMatchupService(),
			rating_service = LocalRatingService(),
			profile_service = LocalProfileService(),
			tournament_service = LocalTournamentService()
	):
		self.competitor_service = competitor_service
		self.matchup_service = matchup_service
		self.rating_service = rating_service
		self.profile_service = profile_service
		self.tournament_service = tournament_service

	def choose_random_competitors(
		self, competitors_list, participants
	):
		competitors_list = list(competitors_list)
		participants = int(participants)
		participants_list = random.sample(competitors_list, participants)
		return participants_list
	
	def get_tournaments_base(self):
		tournaments = self.tournament_service.get_tournaments()
		return tournaments
	
	def get_competitors_info(self, tournament_id):
		tournament = self.tournament_service.get_tournament(tournament_id)
		tournament_competitors = tournament.competitors.all()
		competitors = [obj.competitor_id for obj in tournament_competitors]
		return competitors
