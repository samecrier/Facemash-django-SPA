from django.db import transaction
from django.db.models.functions import Coalesce
from django.db.models import Value
from abc import ABC, abstractmethod
from apps.tournaments.models import TournamentBase, TournamentCompetitor, TournamentRound, RoundCompetitor, TournamentMatchup, TournamentSystem, TournamentRatingSystem, TemplateTournament, TemplateRound


class TournamentService(ABC):

	@abstractmethod
	def get_tournament_obj(self, *args, **kwargs):
		pass


class LocalTournamentService(TournamentService):
	
	def get_tournament_by_string(self, tournament_id):
		return TournamentBase.objects.filter(id=tournament_id).first()
	
	def get_tournament_obj(self, tournament_id):
		if isinstance(tournament_id, TournamentBase):
			return TournamentBase.objects.filter(id=tournament_id.id).first()
		if isinstance(tournament_id, (str, int)):
			return self.get_tournament_by_string(tournament_id)
	
	def get_tournaments(self, order_by=None):
		if order_by:
			return TournamentBase.objects.all().order_by(order_by)
		return TournamentBase.objects.all()
		
	def create_tournament_base(self, profile_id, competitors_number, rounds_number):
		tournament_base = TournamentBase.objects.create(
			profile_id=profile_id,
			competitors_number=competitors_number,
			competitors_remaining=competitors_number,
			rounds_number=rounds_number
		)
		tournament_obj = self.get_tournament_obj(tournament_base)
		return tournament_obj

	def create_tournament_round(self, tournament_base_id, competitors_in_matchup, round_number):
		tournament_round = TournamentRound.objects.create(
			tournament_base_id=tournament_base_id,
			competitors_in_matchup=competitors_in_matchup,
			round_number=round_number
		)
		return tournament_round

	def create_tournament_competitor(self, tournament_base_id, competitor_id):
		tournament_competitor = TournamentCompetitor.objects.create(
			tournament_base_id=tournament_base_id,
			competitor_id=competitor_id,
		)
		return tournament_competitor

	def create_round_competitor(self, tournament_round_id, tournament_competitor_id):
		round_competitor = RoundCompetitor.objects.create(
			tournament_round_id=tournament_round_id,
			tournament_competitor_id=tournament_competitor_id,
		)
		return round_competitor
	
	def create_tournament_matchup(self, round_obj, matchup_number):
		matchup = TournamentMatchup.objects.create(
			tournament_round_id=round_obj,
			matchup_number=matchup_number
		)
		return matchup
	
	def change_round_competitor_status(self, round_competitor_obj, status):
		round_competitor_obj.status=status
		round_competitor_obj.save()
		return round_competitor_obj
	
	def add_competitors_to_matchup(self, matchup_obj, matchup_competitors):
		for competitor in matchup_competitors:
			self.change_round_competitor_status(competitor, 'in schedule')
		matchup_obj.competitors_in_matchup.set(matchup_competitors)
	
	def get_round_matchups(self, round_obj):
		return round_obj.round_matchups.all()
	
	def generate_round_matchups(self, round_obj, round_competitors):
		competitors_in_matchup = round_obj.competitors_in_matchup
		matchup_number = 0
		for i, round_competitor in enumerate(round_competitors):
			if i % competitors_in_matchup == 0:
				matchup_number = matchup_number+1
				matchup = self.create_tournament_matchup(round_obj, matchup_number)
			matchup.competitors_in_matchup.add(round_competitor)
			self.change_round_competitor_status(round_competitor, 'in schedule')
		return self.get_round_matchups(round_obj)

	def get_round_obj_by_tournament_obj(self, tournament_obj, round_number):
		round_obj = tournament_obj.rounds.filter(round_number=round_number).first()
		return round_obj
	
	def get_round_obj_by_tournament_string(self, tournament_id, round_number):
		tournament_obj = self.get_tournament_by_string(tournament_id)
		round_obj = tournament_obj.rounds.filter(round_number=round_number).first()
		return round_obj

	def get_matchup_obj_by_round(self, round_obj, matchup_number):
		matchup_obj = round_obj.round_matchups.filter(matchup_number=matchup_number).first()
		return matchup_obj

	def get_matchup_by_string(self, matchup_id):
		return TournamentMatchup.objects.filter(id=matchup_id).first()
	
	def get_matchup_obj_by_id(self, matchup_id):
		matchup_obj = self.get_matchup_by_string(matchup_id)
		return matchup_obj
	
	def update_status_round(self, round_obj, status):
		round_obj.status = status
		round_obj.save()

	def next_round(self, tournament_obj, round_number):
		next_rounds = tournament_obj.rounds.filter(round_number__gt=round_number).order_by('round_number')
		if not next_rounds:
			return None
		else:
			return next_rounds[0]
	
	def get_winner_tournament_competitor(self, tournament_obj):
		return tournament_obj.competitors.filter(status='active').first()

	def update_winner(self, tournament_competitor_obj):
		tournament_competitor_obj.status = 'winner'
		tournament_competitor_obj.final_position = 1
		tournament_competitor_obj.save()
		return tournament_competitor_obj

	def update_tournament_status(self, tournament_base_obj, winner_obj):
		tournament_base_obj.status= 'completed'
		tournament_base_obj.winner_id = winner_obj.competitor_id
		tournament_base_obj.save()

	def sort_competitors_with_null(self, obj, number=None):
		if number:
			return obj.competitors.all().order_by(Coalesce('final_position', Value(0)))[:number]
		return obj.competitors.all().order_by(Coalesce('final_position', Value(0)))

class APITournamentService(TournamentService):
	
	def get_tournament_obj(self):
		pass
