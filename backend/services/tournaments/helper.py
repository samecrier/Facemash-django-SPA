from django.db import transaction
from django.shortcuts import redirect
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
	
	def get_tournaments_base(self, profile_obj):
		tournaments = self.tournament_service.get_tournaments_profile(profile_id=profile_obj, order_by='updated_at')
		data = {
			'completed_tournaments': dict(),
			'in_progress_tournaments': dict(),
		}
		for i, tournament in enumerate(tournaments):
			if tournament.status == 'completed':
				data['completed_tournaments'][i] = {}
				data['completed_tournaments'][i]['tournament_id'] = tournament.id
				data['completed_tournaments'][i]['status'] = 'completed'
				data['completed_tournaments'][i]['winner_id'] = tournament.winner_id
				data['completed_tournaments'][i]['actual_round'] = None
			else:
				data['in_progress_tournaments'][i] = {}
				data['in_progress_tournaments'][i]['tournament_id'] = tournament.id  # Турниры в процессе
				data['in_progress_tournaments'][i]['status'] = tournament.status
				actual_round = self.get_actual_round_obj_by_tournament(tournament)
				data['in_progress_tournaments'][i]['winner_id'] = None
				data['in_progress_tournaments'][i]['actual_round'] = actual_round.round_number
		return data
	
	def get_tournament_obj(self, tournament_id):
		return self.tournament_service.get_tournament_obj(tournament_id)
	
	def get_competitors_info(self, tournament_id, number=None):
		tournament = self.tournament_service.get_tournament_obj(tournament_id)
		tournament_competitors = self.tournament_service.sort_competitors_with_null(tournament, number)
		competitors = [(obj.competitor_id, obj.final_position) for obj in tournament_competitors]
		return competitors

	def get_rounds(self, tournament_obj):
		print(tournament_obj)
		rounds_obj = tournament_obj.rounds.all()
		return rounds_obj
	
	def get_rounds_status(self, tournament_obj):
		if isinstance(tournament_obj, (int, str)):
			tournament_obj = self.tournament_service.get_tournament_obj(tournament_obj)
		rounds = self.get_rounds(tournament_obj)
		rounds_status = {round: round.status
			for round in sorted(rounds, key=lambda r: r.round_number)}
		return rounds_status
	
	def actual_rounds_status(self, tournament_id):
		tournament_obj = self.tournament_service.get_tournament_obj(tournament_id)
		rounds_status = self.get_rounds_status(tournament_obj)
		previous_status = None
		actual_rounds_status = {}
		for round_obj in rounds_status:
			if round_obj.status != 'not started' or previous_status == 'completed':
				actual_rounds_status[round_obj] = round_obj.status
				previous_status = actual_rounds_status[round_obj]
			else:
				break
		return actual_rounds_status

	
	def get_certain_round_obj(self, tournament_id, round_number):
		tournament_obj = self.tournament_service.get_tournament_obj(tournament_id)
		if not tournament_obj:
			report_message = 'Такого турнира не существует'
			return report_message
		round_obj = self.tournament_service.get_round_obj_by_tournament_obj(tournament_obj, round_number)
		if not round_obj:
			report_message = 'Такого раунда не существует'
			return report_message
		return round_obj
	
	def get_count_matchup_in_round(self, tournament_id, round_number):
		round_obj = self.tournament_service.get_round_obj_by_tournament_string(tournament_id, round_number)
		matchups_in_round = len(round_obj.round_matchups.all())
		return matchups_in_round

	def get_certain_matchup_obj(self, round_obj, matchup_number):
		round_obj = self.tournament_service.get_matchup_obj_by_round(round_obj, matchup_number)
		return round_obj
	
	def get_actual_round_obj_by_tournament(self, tournament_id):
		tournament_obj = self.tournament_service.get_tournament_obj(tournament_id)
		rounds_status = self.get_rounds_status(tournament_obj)
		if list(rounds_status.values())[-1] == 'completed':
			# raise ValueError("Взят завершенный турнир")
			return None 
		for round in rounds_status:
			if rounds_status[round] in ('not started', 'in progress'):
				return round

	def data_type_matchup(self, matchup_obj):
		data = {}
		for i, round_competitor in enumerate(matchup_obj.competitors_in_matchup.all()):
			competitor = round_competitor.tournament_competitor_id.competitor_id
			data[f'{i}_id'] = competitor.id
		return data
	
	def end_tournament(self, tournament_base_obj):
		winner_obj = self.tournament_service.get_winner_tournament_competitor(tournament_base_obj)
		update_winner = self.tournament_service.update_winner(winner_obj)
		self.tournament_service.update_tournament_status(tournament_base_obj, update_winner)

	def turn_next_round(self, tournament_id, round_number):
		tournament_obj = self.tournament_service.get_tournament_obj(tournament_id)
		if tournament_obj.winner_id:
			return None
		round_obj = self.tournament_service.get_round_obj_by_tournament_obj(tournament_obj, round_number)
		self.tournament_service.update_status_round(round_obj, 'completed')
		next_round_obj = self.tournament_service.next_round(tournament_obj, round_number)
		if not next_round_obj:
			self.end_tournament(tournament_obj)
			return None
		else:
			next_round_competitors = tournament_obj.competitors.filter(status='active').order_by('?')
			for next_round_competitor in next_round_competitors:
				self.tournament_service.create_round_competitor(next_round_obj, next_round_competitor)
			return next_round_obj.round_number
	
	def get_winner_competitor_obj(self, tournament_obj):
		tournament = self.tournament_service.get_tournament_obj(tournament_obj)
		return tournament.winner_id
	
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
		check_previous_round = self.tournament_service.get_round_obj_by_tournament_obj(tournament_obj, previous_round_number)
		if not check_previous_round:
			raise AttributeError("А как у тебя проскачил сюда раунд, которого не существует?")
		if check_previous_round.status == 'completed':
			return True
		else:
			return False
		
	def get_actual_rounds(self, tournament_id):
		tournament_obj = self.tournament_service.get_tournament_obj(tournament_id)
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

	@transaction.atomic
	def get_stage_matchups(self, round_obj):
		matchups = self.get_matchups_from_round_obj(round_obj, 'matchup_number')
		if not matchups:
			round_competitors = list(round_obj.round_competitors.all())
			if not round_competitors:
				return None
			random.shuffle(round_competitors)
			matchups = self.tournament_service.generate_round_matchups(round_obj, round_competitors)
		return matchups

		#тут нужен код который будет возвращать первый матчап без winner
		#расчитать матчап winner_id losers_id и поменять им статус в round_competitor на соответствующий