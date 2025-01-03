from django.db import transaction
from django.shortcuts import redirect
from services.competitors.service import LocalCompetitorService
from services.matchups.service import LocalMatchupService
from services.ratings.service import LocalRatingService
from services.profiles.service import LocalProfileService
from services.tournaments.service import LocalTournamentService
import random
from collections import defaultdict

class TournamentHelper:

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

	def get_tournament_obj(self, tournament_id):
		"""Возвращает объект Tournmanet"""
		return self.tournament_service.base.get_tournament_obj(tournament_id)

	def get_certain_matchup_obj(self, round_obj, matchup_number):
		round_obj = self.tournament_service.matchup.get_matchup_obj_by_round_obj(round_obj, matchup_number)
		return round_obj

	def data_type_matchup(self, matchup_obj):
		data = {}
		for i, round_competitor in enumerate(matchup_obj.competitors_in_matchup.all()):
			competitor = round_competitor.tournament_competitor_id.competitor_id
			data[f'{i}_id'] = competitor.id
		return data
	
	def end_tournament(self, tournament_base_obj):
		winner_obj = self.tournament_service.base.get_winner_tournament_competitor(tournament_base_obj)
		self.tournament_service.base.update_winner(winner_obj)
		self.tournament_service.base.update_tournament_status(tournament_base_obj, winner_obj)

	def turn_next_round(self, tournament_id, round_number):
		tournament_obj = self.tournament_service.base.get_tournament_obj(tournament_id)
		if tournament_obj.winner_id:
			return None
		round_obj = self.tournament_service.round.get_round_obj_by_tournament(tournament_obj, round_number)
		self.tournament_service.round.update_status_round(round_obj, 'completed')
		next_round_obj = self.tournament_service.round.get_next_round_obj(tournament_obj, round_number)
		if not next_round_obj:
			self.end_tournament(tournament_obj)
			return None
		else:
			next_round_competitors = tournament_obj.competitors.filter(status='active').order_by('?')
			for next_round_competitor in next_round_competitors:
				self.tournament_service.round.create_round_competitor(next_round_obj, next_round_competitor)
			return next_round_obj.round_number
	
	def get_winner_competitor_obj(self, tournament_obj):
		return tournament_obj.winner_id
	
	def get_matchups_from_round_obj(self, round_obj, order_by=None):
		if order_by:
			return round_obj.round_matchups.all().order_by(order_by)
		return round_obj.round_matchups.all()
	
	def get_actual_matchup(self, round_obj, matchup_number=None):
		if not matchup_number:
			actual_matchups_in_round = round_obj.round_matchups.filter(winner_id__isnull=True).order_by('matchup_number')
			if actual_matchups_in_round:
				for matchup in actual_matchups_in_round:
					if not matchup.winner_id:
						matchup_number = matchup.matchup_number
						break
			else:
				return (None, None)
		matchup_obj = self.get_certain_matchup_obj(round_obj, matchup_number)
		if not matchup_obj:
			return (None, None)
		data_matchup = self.data_type_matchup(matchup_obj)
		return (data_matchup, matchup_obj)
	
	def check_actuality_round_obj(self, tournament_obj, round_obj):
		previous_round_number = (round_obj.round_number - 1)
		if previous_round_number == 0:
			return True
		check_previous_round = self.tournament_service.round.get_round_obj_by_tournament(tournament_obj, previous_round_number)
		if not check_previous_round:
			raise AttributeError("А как у тебя проскачил сюда раунд, которого не существует?")
		if check_previous_round.status == 'completed':
			return True
		else:
			return False

	def get_actual_rounds(self, tournament_id):
		tournament_obj = self.tournament_service.base.get_tournament_obj(tournament_id)
		actual_rounds = tournament_obj.rounds.exclude(status='not started')
		return actual_rounds
	
	def check_correct_tournament_information(self, participants, rounds, in_matchup):
		participants = int(participants)
		rounds = int(rounds)
		in_matchup = int(in_matchup)
		equation = (in_matchup ** rounds == participants)
		if equation:
			return True
		else:
			return False

	def generate_round_matchups(self, round_obj, round_competitors):
		competitors_in_matchup = round_obj.competitors_in_matchup
		matchup_number = 0
		for i, round_competitor in enumerate(round_competitors):
			if i % competitors_in_matchup == 0:
				matchup_number = matchup_number+1
				matchup = self.tournament_service.matchup.create_tournament_matchup(round_obj, matchup_number)
			self.tournament_service.matchup.update_matchup_competitors(matchup, round_competitor)
			self.tournament_service.round.update_round_competitor_status(round_competitor, 'in schedule')
		return self.tournament_service.matchup.get_matchups_by_round_obj(round_obj)

	@transaction.atomic
	def get_stage_matchups(self, round_obj):
		matchups = self.get_matchups_from_round_obj(round_obj, 'matchup_number')
		if not matchups:
			round_competitors = list(round_obj.round_competitors.all())
			if not round_competitors:
				return None
			random.shuffle(round_competitors)
			matchups = self.generate_round_matchups(round_obj, round_competitors)
		return matchups

		#тут нужен код который будет возвращать первый матчап без winner
		#расчитать матчап winner_id losers_id и поменять им статус в round_competitor на соответствующий