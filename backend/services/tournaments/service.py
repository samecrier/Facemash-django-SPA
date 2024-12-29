from django.db import transaction
from django.db.models.functions import Coalesce
from django.db.models import Value, Prefetch
from abc import ABC, abstractmethod
from services.helpers import debug_queries
from apps.tournaments.models import *


class BaseService:
	
	def get_obj_by_string(self, model, identifier):
		return model.objects.filter(id=identifier).first()
	
	def get_object(self, model, identifier):
		if isinstance(identifier, model):
			return model.objects.filter(id=identifier.id).first() #это используется, чтобы возвращать конкретно запись из базы с обновленными типами (str->int и.т.д)
		elif isinstance(identifier, (str, int)):
			return self.get_obj_by_string(model, identifier)
	
	def get_service(self, service_class):
		return service_class()


class TournamentBaseService(BaseService):

	def get_tournament_prefetch(self, tournament_id):
		return TournamentBase.objects.prefetch_related('competitors__competitor_id').get(id=tournament_id)
	
	def get_tournament_obj(self, tournament):
		return self.get_object(TournamentBase, tournament)
	
	def get_tournaments(self, order_by=None): #Не используется
		"""Возвращает все турниры без привязки к профайлу"""
		if order_by:
			return TournamentBase.objects.all().order_by(order_by)
		return TournamentBase.objects.all()
	
	def get_tournaments_by_profile(self, profile, order_by=None):
		"""Возвращает по profile(int или obj) все его турниры"""
		if order_by:
			return TournamentBase.objects.filter(profile_id=profile).order_by(order_by)
		return TournamentBase.objects.filter(profile_id=profile)
	
	def get_winner_tournament_competitor(self, tournament_obj):
		return tournament_obj.competitors.filter(status='active').first()
	
	def create_tournament_base(self, profile_id, competitors_qty, rounds_qty):
		competitors_qty, rounds_qty = int(competitors_qty), int(rounds_qty)
		tournament_base = TournamentBase.objects.create(
			profile_id=profile_id,
			competitors_qty=competitors_qty,
			competitors_remaining=competitors_qty,
			rounds_qty=rounds_qty
		)
		tournament_obj = self.get_tournament_obj(tournament_base)
		return tournament_obj

	def create_tournament_competitor(self, tournament_base_id, competitor_id):
		tournament_competitor = TournamentCompetitor.objects.create(
			tournament_base_id=tournament_base_id,
			competitor_id=competitor_id,
		)
		return tournament_competitor
	
	def update_winner(self, tournament_competitor_obj):
		tournament_competitor_obj.status = 'winner'
		tournament_competitor_obj.final_position = 1
		tournament_competitor_obj.save()

	def update_tournament_status(self, tournament_base_obj, winner_obj):
		tournament_base_obj.status= 'completed'
		tournament_base_obj.winner_id = winner_obj.competitor_id
		tournament_base_obj.save()

	@debug_queries
	def sort_competitors_with_null(self, tournament_obj, number=None):
		if number:
			return tournament_obj.competitors.select_related(
				'competitor_id__city',
				'competitor_id__rating'
			).order_by(
				Coalesce('final_position', Value(0))
			)[:number]
		return tournament_obj.competitors.select_related(
				'competitor_id__city',
				'competitor_id__rating'
			).order_by(Coalesce('final_position', Value(0)), "-competitor_id__rating__rating", "competitor_id")

	def get_sorted_competitors_queryset(self):
		return TournamentCompetitor.objects.select_related(
			'competitor_id__city',
			'competitor_id__rating'
		).order_by(Coalesce('final_position', Value(0)), "-competitor_id__rating__rating", "competitor_id")
	
	def get_competitors_queryset(self):
		return TournamentCompetitor.objects.select_related(
			'competitor_id__city',
			'competitor_id__rating'
		)
	
	def get_competitors_prefetch(self, sorted=False):
		if sorted:
			return Prefetch(
				'competitors',
				queryset=self.get_sorted_competitors_queryset(),
				to_attr="sorted_competitors"
			) 
		return Prefetch(
				'competitors',
				queryset=self.get_competitors_queryset(),
			) 

class TournamentRoundService(BaseService):
	
	def get_round_obj(self, round):
		return self.get_object(TournamentRound, round)
	
	def get_rounds_objs(self, tournament_obj):
		rounds_obj = tournament_obj.rounds.all()
		return rounds_obj
	
	def get_round_obj_by_tournament(self, tournament, round_number):
		"""Tournament obj или id(str) возвращает объект раунда"""
		tournament_obj = self.get_object(TournamentBase, tournament)
		round_obj = tournament_obj.rounds.filter(round_number=round_number).first()
		return round_obj
	
	def get_next_round_obj(self, tournament_obj, round_number):
		next_rounds = tournament_obj.rounds.filter(round_number__gt=round_number).order_by('round_number')
		if not next_rounds:
			return None
		else:
			return next_rounds[0]

	def create_tournament_round(self, tournament_base_id, competitors_in_matchup, round_number):
		competitors_in_matchup, round_number = int(competitors_in_matchup), int(round_number)
		tournament_round = TournamentRound.objects.create(
			tournament_base_id=tournament_base_id,
			competitors_in_matchup=competitors_in_matchup,
			round_number=round_number
		)
		round_obj = self.get_round_obj(tournament_round)
		return round_obj
	
	def create_round_competitor(self, tournament_round_id, tournament_competitor_id):
		round_competitor = RoundCompetitor.objects.create(
			tournament_round_id=tournament_round_id,
			tournament_competitor_id=tournament_competitor_id,
		)
		return round_competitor
	
	def update_round_competitor_status(self, round_competitor_obj, status):
		round_competitor_obj.status=status
		round_competitor_obj.save()
	
	def update_status_round(self, round_obj, status):
		round_obj.status = status
		round_obj.save()

	def update_competitors_qty(self, round_obj):
		round_obj.competitors_qty += 1
		round_obj.save()

	def update_matchups_qty(self, round_obj):
		round_obj.matchups_qty += 1
		round_obj.save()
	
	
class TournamentMatchupService(BaseService):
	
	def get_matchup_obj_by_round_obj(self, round_obj, matchup_number):
		matchup_obj = round_obj.round_matchups.filter(matchup_number=matchup_number).first()
		return matchup_obj
	
	def get_matchup_obj(self, matchup):
		return self.get_object(TournamentMatchup, matchup)
	
	def get_matchups_by_round_obj(self, round_obj):
		return round_obj.round_matchups.all()
	
	def create_tournament_matchup(self, round_obj, matchup_number):
		matchup = TournamentMatchup.objects.create(
			tournament_round_id=round_obj,
			matchup_number=matchup_number
		)
		matchup_obj = self.get_matchup_obj(matchup)
		self.update_round_matchups_qty(matchup_obj)
		return matchup_obj
	
	def update_matchup_competitors(self, matchup_obj, round_competitor):
		matchup_obj.competitors_in_matchup.add(round_competitor)
		round_service = self.get_service(TournamentRoundService)
		round_service.update_competitors_qty(matchup_obj.tournament_round_id)

	def update_round_matchups_qty(self, matchup_obj):
		round_service = self.get_service(TournamentRoundService)
		round_service.update_matchups_qty(matchup_obj.tournament_round_id)


class LocalTournamentService:

	def __init__(self, 
			base=TournamentBaseService(),
			round=TournamentRoundService(),
			matchup=TournamentMatchupService()
			):
		self.base = base
		self.round = round
		self.matchup = matchup


class TournamentManager:
	pass


class APITournamentService:
	pass