from services.competitors.service import LocalCompetitorService
from services.matchups.service import LocalMatchupService
from services.ratings.service import LocalRatingService
from services.profiles.service import LocalProfileService
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
			tournament_service = LocalTournamentService()
	):
		self.competitor_service = competitor_service
		self.matchup_service = matchup_service
		self.rating_service = rating_service
		self.profile_service = profile_service
		self.tournament_service = tournament_service

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
		
		for i, matchup in enumerate(matchups_obj):
			data['matchup_info']['matchup_number'] = matchup_obj.matchup_number
			data['matchup_info']['matchup_winner'] = matchup_obj.winner_id.tournament_competitor_id.competitor_id.id
			if matchup.winner_id:
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
