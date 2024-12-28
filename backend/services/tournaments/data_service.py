from services.competitors.service import LocalCompetitorService
from services.matchups.service import LocalMatchupService
from services.ratings.service import LocalRatingService
from services.profiles.service import LocalProfileService
from services.tournaments.data_helper import TournamentDataHelper
from services.tournaments.helper import TournamentHelper
from services.tournaments.service import LocalTournamentService
from services.helpers import Helper
from collections import defaultdict


class TournamentGetData():

	def __init__(
			self,
			competitor_service = LocalCompetitorService(),
			matchup_service = LocalMatchupService(),
			rating_service = LocalRatingService(),
			profile_service = LocalProfileService(),
			tournament_service = LocalTournamentService(),
			helper_service = TournamentHelper(),
			data_helper_service = TournamentDataHelper()
	):
		self.competitor_service = competitor_service
		self.matchup_service = matchup_service
		self.rating_service = rating_service
		self.profile_service = profile_service
		self.tournament_service = tournament_service
		self.helper_service = helper_service
		self.data_helper_service = data_helper_service

	def get_data_stage(self, request, matchups_obj):
		from django.db import reset_queries  # Для сброса предыдущих запросов

	# Сбросить список запросов
		reset_queries()
		data = {
				'matchups': defaultdict(lambda: defaultdict(lambda: defaultdict(dict))),
				'round_info': defaultdict(dict),
				'matchup_info': defaultdict(dict),
				'tournament_info': defaultdict(dict),
			}
		matchups_obj = matchups_obj.select_related(
			'tournament_round_id',
			'winner_id__tournament_competitor_id__competitor_id'
		)
		
		matchups_obj = matchups_obj.prefetch_related(
			'competitors_in_matchup__tournament_competitor_id__competitor_id__city',
			'competitors_in_matchup__tournament_competitor_id__competitor_id__rating',
			'competitors_in_matchup__tournament_competitor_id__competitor_id__profiles_ratings',
		)

		# Запрос к базе данных происходит только здесь
		matchup_obj = matchups_obj.first()
		round_obj = matchup_obj.tournament_round_id
		round_number = round_obj.round_number
		data['round_info']['round_number'] = round_number
		
		matchups_overall = len(matchups_obj)
		data['matchup_info']['matchups_overall'] = matchups_overall

		tournament_base_obj = round_obj.tournament_base_id
		data['tournament_info']['tournament_id'] = tournament_base_obj.id
		data['tournament_info']['winner_id'] = tournament_base_obj.winner_id
		
		for i, matchup in enumerate(matchups_obj.order_by('matchup_number')):
			if matchup_obj:
				data['matchup_info']['matchup_number'] = matchup_obj.matchup_number
				if matchup.winner_id:
					data['matchup_info']['matchup_winner'] = matchup_obj.winner_id.tournament_competitor_id.competitor_id.id
					data['matchups'][matchup.matchup_number]['status'] = 'сыгран'
				else:
					data['matchups'][matchup.matchup_number]['status'] = 'в ожидании'
				
			for i, competitor in enumerate(matchup.competitors_in_matchup.all()):
				round_competitor_obj = competitor
				
				competitor_obj = competitor.tournament_competitor_id.competitor_id
				data['matchups'][matchup.matchup_number]['competitors'][i]['round_competitor_id'] = round_competitor_obj.id
				data['matchups'][matchup.matchup_number]['competitors'][i]['round_competitor_status'] = round_competitor_obj.status
				data['matchups'][matchup.matchup_number]['competitors'][i]['round_competitor_delta_round'] = round_competitor_obj.delta_round
				data['matchups'][matchup.matchup_number]['competitors'][i]['round_competitor_delta_round_profile'] = round_competitor_obj.delta_round_profile
				data['matchups'][matchup.matchup_number]['competitors'][i]['round_competitor_result'] = round_competitor_obj.result

				# data['matchups'][matchup.matchup_number]['competitors'][i]['tournament_competitor_id'] = tournament_competitor_obj.id
				
				data['matchups'][matchup.matchup_number]['competitors'][i]['competitor_id'] = competitor_obj.id
				data['matchups'][matchup.matchup_number]['competitors'][i]['name'] = competitor_obj.name
				data['matchups'][matchup.matchup_number]['competitors'][i]['age'] = competitor_obj.age
				data['matchups'][matchup.matchup_number]['competitors'][i]['city'] = competitor_obj.city.city_eng
				data['matchups'][matchup.matchup_number]['competitors'][i]['rating'] = competitor_obj.rating.rating
				# if request.user.is_authenticated: # эта штука вызывает вопросов и надо реализовывать ее через кэш
				# 	data['matchups'][matchup.matchup_number]['competitors'][i]['rating_profile'] = self.rating_service.get_rating_profile(request.user, competitor_obj)
		
		data_dict = Helper.convert_to_dict(data)
		# for query in connection.queries:
		# 	print(query['sql'])
		
		return data_dict

	def get_tournaments_base(self, profile_obj):
		"""По профилю возвращает data с турнирами профиля в tournamentview"""
		tournaments = self.tournament_service.base.get_tournaments_by_profile(profile_obj, order_by='updated_at')
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
				actual_round = self.data_helper_service.get_actual_round_obj_by_tournament(tournament)
				data['in_progress_tournaments'][i]['winner_id'] = None
				data['in_progress_tournaments'][i]['actual_round'] = actual_round.round_number
		return data
	
	def actual_rounds_status(self, tournament):
		rounds_status = self.data_helper_service.get_rounds_status(tournament)
		previous_status = None
		actual_rounds_status = {}
		for round_obj in rounds_status:
			if round_obj.status != 'not started' or previous_status == 'completed':
				actual_rounds_status[round_obj] = round_obj.status
				previous_status = actual_rounds_status[round_obj]
			else:
				break
		return actual_rounds_status
	
	def get_competitors_rank(self, tournament_id, number=None):
		"""
		Возвращает список кортежей участников турнира с актуальными 
		позициями, где 1 значение это объект Competitor, а 2 - позиция в турнире
		"""
		tournament = self.tournament_service.base.get_tournament_obj(tournament_id)
		tournament_competitors = self.tournament_service.base.sort_competitors_with_null(tournament, number)
		competitors = [(obj.competitor_id, obj.final_position) for obj in tournament_competitors]
		return competitors
	
	def get_actual_round_obj_by_tournament(self, tournament):
		return self.data_helper_service.get_actual_round_obj_by_tournament(tournament)
	
	def get_tournament_info_by_obj(self, tournament_obj):
		tournament_data = {
			'tournament_info': self.data_helper_service.get_tournament_info_dict(tournament_obj),
			'rounds_info': self.data_helper_service.get_rounds_info_dict(tournament_obj),
			'tournament_competitors': self.data_helper_service.get_tournament_competitors_dict(tournament_obj),
		}
		return tournament_data
	
	def get_round_info_by_obj(self, round_obj):
		tournament_obj = round_obj.tournament_base_id
		round_data = {
			'tournament_info': self.data_helper_service.get_tournament_info_dict(tournament_obj),
			'round_info': self.data_helper_service.get_round_info_dict(round_obj),
			'round_competitors': self.data_helper_service.get_round_competitors_dict(round_obj)
		}
		return round_data
	
	def get_matchup_info_by_obj(self, matchup_obj):
		round_obj = matchup_obj.tournament_round_id
		tournament_obj = round_obj.tournament_base_id

		matchup_data = {
			'tournament_info': self.data_helper_service.get_tournament_info_dict(tournament_obj),
			'round_info': self.data_helper_service.get_round_info_dict(round_obj),
			'matchup_info': self.data_helper_service.get_matchup_info_dict(matchup_obj),
			'matchup_competitors': self.data_helper_service.get_matchup_competitors_dict(matchup_obj)
		}
		
		return matchup_data