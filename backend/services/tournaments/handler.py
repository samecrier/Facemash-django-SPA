from django.db import transaction
from services.competitors.service import LocalCompetitorService
from services.matchups.service import LocalMatchupService
from services.ratings.service import LocalRatingService
from services.profiles.service import LocalProfileService
from services.tournaments.service import LocalTournamentService
from services.tournaments.helper import TournamentHelper
from services.matchups.handler import MatchupHandler
from services.ratings.rating_systems import EloRatingSystem32, EloRatingSystem64

class TournamentHandler():
	
	def __init__(
			self,
			competitor_service = LocalCompetitorService(),
			matchup_service = LocalMatchupService(),
			rating_service = LocalRatingService(),
			profile_service = LocalProfileService(),
			tournament_service = LocalTournamentService(),
			tournament_helper = TournamentHelper(),
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
			tournament_obj, round_obj = self.initiate_of_tournament(profile_id, competitor_for_tournament, participants, rounds, in_matchup)
			tournament_id = tournament_obj.id
			round_number = round_obj.round_number
			return (tournament_id, round_number)
	
	def initiate_of_tournament(self, profile_id, competitors, participants, rounds, in_matchup):
		tournament_obj = self.tournament_service.create_tournament_base(
			profile_id=profile_id,
			competitors_number=participants,
			rounds_number=rounds
		)

		for round_number in range(1, tournament_obj.rounds_number+1):
			if round_number == 1:
				round_obj = self.tournament_service.create_tournament_round(
					tournament_base_id=tournament_obj,
					competitors_in_matchup=in_matchup,
					round_number=round_number
				)
			else:
				self.tournament_service.create_tournament_round(
					tournament_base_id=tournament_obj,
					competitors_in_matchup=in_matchup,
					round_number=round_number
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
		return (tournament_obj, round_obj)

	@transaction.atomic
	def process_tournament_matchup(self, request, matchup_id, winner_id, loser_ids):
		rating_systems = {
			'elo_32': EloRatingSystem32()
		}
		matchup_obj = self.tournament_service.get_matchup_obj_by_id(matchup_id)
		if matchup_obj.winner_id:
			raise AttributeError("ПОБЕДИТЕЛЬ УЖЕ ЕСТЬ")
		winner_id = int(winner_id)
		loser_ids = [int(loser_id) for loser_id in loser_ids]
		delta_data = {loser_id:0 for loser_id in loser_ids}
		delta_data[winner_id] = 0
		round_obj = matchup_obj.tournament_round_id
	
		matchup_handler = MatchupHandler(
			request=request,
			winner_id = winner_id,
			loser_id=loser_ids,
			rating_system=rating_systems[round_obj.rating_system],
			tournament_matchup_id=matchup_obj
		)
		matchup_handler.process_matchup()

		tournament_base = matchup_obj.tournament_round_id.tournament_base_id
		if tournament_base.status == 'not started':
			tournament_base.status = 'in progress'
			tournament_base.save()
		for round_competitor in matchup_obj.competitors_in_matchup.all():
			competitor = round_competitor.tournament_competitor_id.competitor_id
			tournament_competitor = round_competitor.tournament_competitor_id
			if competitor.id == winner_id:
				round_competitor.result = 1
				round_competitor.status = 'qualified'
				round_competitor.delta_round = matchup_handler.delta[competitor]
				round_competitor.delta_round_profile = matchup_handler.delta_profile[competitor]
				tournament_competitor.delta_tournament += matchup_handler.delta[competitor]
				tournament_competitor.delta_tournament_profile += matchup_handler.delta_profile[competitor]
				if tournament_competitor.status == 'not started':
					tournament_competitor.status = 'active'
				matchup_obj.winner_id = round_competitor
			else:
				matchup_obj.losers.add(round_competitor)
				round_competitor.result = 0
				tournament_competitor.status = 'eliminated'
				round_competitor.status = 'eliminated'
				round_competitor.delta_round = matchup_handler.delta[competitor]
				round_competitor.delta_round_profile = matchup_handler.delta_profile[competitor]
				tournament_competitor.delta_tournament += matchup_handler.delta[competitor]
				tournament_competitor.delta_tournament_profile += matchup_handler.delta_profile[competitor]
				tournament_competitor.final_position = tournament_base.competitors_remaining
				tournament_base.competitors_remaining = tournament_base.competitors_remaining-1
				tournament_base.save()
			
			tournament_competitor.save()
			round_competitor.save()
			matchup_obj.save()

		print(matchup_id, '/', winner_id)