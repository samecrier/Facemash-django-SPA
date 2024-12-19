from django.db import transaction
from abc import ABC, abstractmethod
from apps.tournaments.models import TournamentBase, TournamentCompetitor, TournamentRound, RoundCompetitor, TournamentMatchup, TournamentSystem, TournamentRatingSystem, TemplateTournament, TemplateRound


class TournamentService(ABC):

	@abstractmethod
	def get_tournament(self, *args, **kwargs):
		pass


class LocalTournamentService(TournamentService):
	
	def get_tournament(self, tournament_id):
		return TournamentBase.objects.get(id=tournament_id)
	
	def get_tournaments(self):
		return TournamentBase.objects.all()
	
	def create_tournament_base(self, profile_id, competitors_number, rounds_number):
		tournament_base, created = TournamentBase.objects.get_or_create(
			profile_id=profile_id,
			competitors_number=competitors_number,
			rounds_number=rounds_number
		)
		return tournament_base

	def create_tournament_round(self, tournament_base_id, competitors_in_matchup):
		tournament_round, created = TournamentRound.objects.get_or_create(
			tournament_base_id=tournament_base_id,
			competitors_in_matchup=competitors_in_matchup
		)
		return tournament_round

	def create_tournament_competitor(self, tournament_base_id, competitor_id):
		tournament_competitor, created = TournamentCompetitor.objects.get_or_create(
			tournament_base_id=tournament_base_id,
			competitor_id=competitor_id,
		)
		return tournament_competitor

	def create_round_competitor(self, tournament_competitor_id, tournament_round_id):
		round_competitor, created = RoundCompetitor.objects.get_or_create(
			tournament_competitor_id=tournament_competitor_id,
			tournament_round_id=tournament_round_id,
		)
		return round_competitor

class APITournamentService(TournamentService):
	
	def get_tournament(self):
		pass
