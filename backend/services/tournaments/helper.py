from django.db import transaction
from services.competitors.service import LocalCompetitorService
from services.matchups.service import LocalMatchupService
from services.ratings.service import LocalRatingService
from services.profiles.service import LocalProfileService
from services.tournaments.service import LocalTournamentService
import random
from collections import defaultdict

class TournamentHelper():

	def __init__(
			self,
			competitor_service=LocalCompetitorService(),
			matchup_service=LocalMatchupService(),
			rating_service=LocalRatingService(),
			profile_service=LocalProfileService(),
			tournament_service=LocalTournamentService(),
			
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
		tournament = self.tournament_service.get_tournament_obj(tournament_id)
		tournament_competitors = tournament.competitors.all()
		competitors = [obj.competitor_id for obj in tournament_competitors]
		return competitors

	def get_rounds(self, tournament_obj):
		rounds_obj = tournament_obj.rounds.all()
		return rounds_obj
	
	def get_rounds_status(self, tournament_obj):
		rounds = self.get_rounds(tournament_obj)
		rounds_status = {round.round_number: round.status
			for round in sorted(rounds, key=lambda r: r.round_number)}
		return rounds_status
	
	def get_certain_round_obj(self, tournament_id, round_number):
		tournament_obj = self.tournament_service.get_tournament_obj(tournament_id)
		round_obj = self.tournament_service.get_round_obj(tournament_obj, round_number)
		return round_obj

	def get_certain_matchup_obj(self, round_obj, matchup_number):
		round_obj = self.tournament_service.get_matchup_obj_by_round(round_obj, matchup_number)
		return round_obj
	
	def get_actual_round_obj_by_tournament(self, tournament_id):
		tournament_obj = self.tournament_service.get_tournament_by_string(tournament_id)
		rounds_status = self.get_rounds_status(tournament_obj)
		if list(rounds_status.values())[-1] == 'completed':
			raise ValueError("Взят завершенный турнир")
		for round in rounds_status:
			if rounds_status[round] == 'not started':
				return self.get_certain_round_obj(tournament_id, round)
			elif rounds_status[round] == 'in progress':
				return self.get_certain_round_obj(tournament_id, round)
		
	def data_type_matchup(self, matchup_obj):
		data = {}
		for i, round_competitor in enumerate(matchup_obj.competitors_in_matchup.all()):
			competitor = round_competitor.tournament_competitor_id.competitor_id
			data[f'{i}_id'] = competitor.id
		return data
	
	def get_actual_matchup(self, tournament_id, round_number, matchup_number=0):
		round_obj = self.get_certain_round_obj(tournament_id, round_number)
		for matchup in round_obj.round_matchups.all().order_by('matchup_number'):
			if not matchup.winner_id:
				matchup_number = matchup.matchup_number
				break
		matchup_obj = self.get_certain_matchup_obj(round_obj, matchup_number)
		data_matchup = self.data_type_matchup(matchup_obj)
		return (data_matchup, matchup_obj)
	
	@transaction.atomic
	def get_actual_matchups(self, round_obj):
		matchups = list(round_obj.round_matchups.all())
		if not matchups:
			round_competitors = list(round_obj.round_competitors.all())
			random.shuffle(round_competitors)
			matchups = self.tournament_service.generate_round_matchups(round_obj, round_competitors)

		#тут нужен код который будет возвращать первый матчап без winner
		#расчитать матчап winner_id losers_id и поменять им статус в round_competitor на соответствующий