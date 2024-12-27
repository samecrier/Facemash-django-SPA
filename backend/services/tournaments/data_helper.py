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
	
	def get_actual_round_obj_by_tournament(self, tournament_id):
		tournament_obj = self.tournament_service.base.get_tournament_obj(tournament_id)
		rounds_status = self.get_rounds_status(tournament_obj)
		if list(rounds_status.values())[-1] == 'completed':
			# raise ValueError("Взят завершенный турнир")
			return None 
		for round in rounds_status:
			if rounds_status[round] in ('not started', 'in progress'):
				return round