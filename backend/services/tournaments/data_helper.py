from services.helpers import debug_queries, measure_time
from services.tournaments.service import LocalTournamentService

class TournamentDataHelper():
	
	def __init__(self, tournament_service=LocalTournamentService()):
		self.tournament_service = tournament_service

	def get_rounds_status(self, tournament):
		"""Возвращает dict со статусами всех раундов турнира в порядке
		возрастанию раунда
		"""
		tournament_obj = self.tournament_service.base.get_tournament_obj(tournament)
		rounds = self.tournament_service.round.get_rounds_objs(tournament_obj)
		rounds_status = {round: round.status
			for round in sorted(rounds, key=lambda r: r.round_number)}
		return rounds_status
	
	def get_actual_round_number_by_tournament(self, tournament_id):
		tournament_obj = self.tournament_service.base.get_tournament_obj(tournament_id)
		rounds_status = self.get_rounds_status(tournament_obj)
		if list(rounds_status.values())[-1] == 'completed':
			# raise ValueError("Взят завершенный турнир")
			return None 
		for round in rounds_status:
			if rounds_status[round] in ('not started', 'in progress'):
				return round.round_number
	
	def get_competitor_info_dict(self, competitor_obj):
		competitor_info = {
			'id': competitor_obj.id,
			'name': competitor_obj.name,
			'name_id': competitor_obj.name_id,
			'age': competitor_obj.age,
			'city': competitor_obj.city.city_eng,
			'rating': competitor_obj.rating.rating,
		}
		return competitor_info

	@debug_queries
	def get_tournament_info_dict(self, tournament_obj):
		tournament_info = {
			'id': tournament_obj.id,
			'profile_id': tournament_obj.profile_id.id,
			'actual_round_number': self.get_actual_round_number_by_tournament(tournament_obj),
			'competitors_qty': tournament_obj.competitors_qty,
			'competitors_remaining': tournament_obj.competitors_remaining,
			'rounds_qty': tournament_obj.rounds_qty,
			'winner_id': tournament_obj.winner_id.id if tournament_obj.winner_id else None,
			'created_at': tournament_obj.created_at,
			'updated_at': tournament_obj.updated_at

		}
		return tournament_info
	
	def get_round_info_dict(self, round_obj):
		round_info = {
			'round_number': round_obj.round_number,
			'competitors_qty': round_obj.competitors_qty,
			'matchups_qty': round_obj.matchups_qty,
			'rating_system': round_obj.rating_system,
			'competitors_in_matchup': round_obj.competitors_in_matchup,
			'status': round_obj.status,
			'created_at': round_obj.created_at,
			'updated_at': round_obj.updated_at,
		}
		return round_info

	def get_tournament_competitor_info_dict(self, tournament_competitor_obj):
		tournament_competitor_info = {
			'id': tournament_competitor_obj.id,
			'status': tournament_competitor_obj.status, 
			'final_position': tournament_competitor_obj.final_position, 
			'delta_tournament': tournament_competitor_obj.delta_tournament, 
			'delta_tournament_profile': tournament_competitor_obj.delta_tournament_profile, 
		}
		return tournament_competitor_info
	
	@measure_time
	@debug_queries
	def get_tournament_competitors_dict(self, tournament_obj):
		competitors = {}
		for t_competitor_obj in self.tournament_service.base.sort_competitors_with_null(tournament_obj):
		# for t_competitor_obj in tournament_obj.sorted_competitors:
			competitor_obj = t_competitor_obj.competitor_id
			competitors[competitor_obj.id] = {
				'competitor_info': self.get_competitor_info_dict(competitor_obj),
				'tournament_info': self.get_tournament_competitor_info_dict(t_competitor_obj)
			}
		return competitors
	
	@debug_queries
	def get_rounds_info_dict(self, tournament_obj):
		rounds_info = {}
		for round_obj in tournament_obj.rounds.all().order_by('round_number'):
			rounds_info[round_obj.round_number] = self.get_round_info_dict(round_obj)
		return rounds_info

	def get_round_competitor_info_dict(self, round_competitor_obj):
		round_competitor_info = {
			'id': round_competitor_obj.id,
			'result': round_competitor_obj.result,
			'status': round_competitor_obj.status,
			'delta_round': round_competitor_obj.delta_round,
			'delta_round_profile': round_competitor_obj.delta_round_profile,
		}
		return round_competitor_info

	def get_round_competitors_dict(self, round_obj):
		round_competitors = {}
		for round_competitor_obj in round_obj.round_competitors.all().order_by('?'):
			competitor_obj = round_competitor_obj.tournament_competitor_id.competitor_id
			tournament_competitor_obj = round_competitor_obj.tournament_competitor_id
			round_competitors[competitor_obj.id] = {
				'competitor_info': self.get_competitor_info_dict(competitor_obj),
				'tournament_info': self.get_tournament_competitor_info_dict(tournament_competitor_obj),
				'round_info': self.get_round_competitor_info_dict(round_competitor_obj)
			}
		return round_competitors

	def get_matchup_info_dict(self, matchup_obj):
		matchup_info = {
			'id': matchup_obj.id,
			'matchup_number': matchup_obj.matchup_number,
			'round_competitor_winner_id': matchup_obj.winner_id if matchup_obj.winner_id else None,
			'competitor_winner_id': matchup_obj.winner_id.tournament_competitor_id.competitor_id.id if matchup_obj.winner_id else None,
			'status': matchup_obj.status
		}
		return matchup_info
	
	def get_matchup_competitors_dict(self, matchup_obj):
		matchup_competitors = {}
		for round_competitor_obj in matchup_obj.competitors_in_matchup.all():
			tournament_competitor_obj = round_competitor_obj.tournament_competitor_id
			competitor_obj = tournament_competitor_obj.competitor_id
			matchup_competitors[competitor_obj.id] = {
				'competitor_info': self.get_competitor_info_dict(competitor_obj),
				'tournament_info': self.get_tournament_competitor_info_dict(tournament_competitor_obj),
				'round_info': self.get_round_competitor_info_dict(round_competitor_obj)
			}
		return matchup_competitors
	
	def get_matchups_dict(self, matchups_obj):
		matchups = {}
		for matchup_obj in matchups_obj.order_by('matchup_number'):
			matchup_number = matchup_obj.matchup_number
			matchups[matchup_number] = {'competitors': {}}
			for i, competitor in enumerate(matchup_obj.competitors_in_matchup.all()):
				round_competitor_obj = competitor
				tournament_competitor_obj = round_competitor_obj.tournament_competitor_id
				competitor_obj = tournament_competitor_obj.competitor_id
				matchups[matchup_number]['competitors'][i] = {}
				matchups[matchup_number]['competitors'][i]['competitor_info'] = self.get_competitor_info_dict(competitor_obj)
				matchups[matchup_number]['competitors'][i]['round_info'] = self.get_round_competitor_info_dict(round_competitor_obj)
				matchups[matchup_number]['competitors'][i]['tournament_info'] = self.get_tournament_competitor_info_dict(tournament_competitor_obj)
				# if request.user.is_authenticated: # эта штука вызывает вопросов и надо реализовывать ее через кэш
				# 	matchups[matchup_number]['competitors'][i]['rating_profile'] = self.rating_service.get_rating_profile(request.user, competitor_obj)
		return matchups