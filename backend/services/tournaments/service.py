from django.db import transaction
from django.db.models.functions import Coalesce
from django.db.models import Value
from django.shortcuts import get_object_or_404
from services.service_helper import StringHelper
from abc import ABC, abstractmethod
from apps.tournaments.models import *

class TournamentManager:
	pass

class TournamentBaseService:

	def get_tournament_obj(self, tournament):
		if isinstance(tournament, TournamentBase):
			return TournamentBase.objects.filter(id=tournament.id).first() #это используется, чтобы возвращать конкретно запись из базы с обновленными типами (str->int и.т.д)
		elif isinstance(tournament, (str, int)):
			return StringHelper.get_obj_by_string(TournamentBase, tournament)
	
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
	
	def create_tournament_base(self, profile_id, competitors_number, rounds_number):
		competitors_number, rounds_number = int(competitors_number), int(rounds_number)
		tournament_base = TournamentBase.objects.create(
			profile_id=profile_id,
			competitors_number=competitors_number,
			competitors_remaining=competitors_number,
			rounds_number=rounds_number
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

	def sort_competitors_with_null(self, tournament_obj, number=None):
		if number:
			return tournament_obj.competitors.all().order_by(Coalesce('final_position', Value(0)))[:number]
		return tournament_obj.competitors.all().order_by(Coalesce('final_position', Value(0)))

class TournamentRoundService:
	
	def get_round_obj(self, round):
		if isinstance(round, TournamentRound):
			return TournamentRound.objects.filter(id=round.id)
		elif isinstance(round, (str, int)):
			return StringHelper.get_obj_by_string(TournamentRound, round)
	
	def get_round_obj_by_tournament(self, tournament, round_number):
		"""Tournament obj или id(str) возвращает объект раунда"""
		if isinstance(tournament, TournamentBase):
			tournament_obj = tournament
		elif isinstance(tournament, (str, int)):
			tournament_obj = StringHelper.get_obj_by_string(TournamentBase, tournament)
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
	
class TournamentMatchupService:
	def get_matchup_obj_by_round_obj(self, round_obj, matchup_number):
		matchup_obj = round_obj.round_matchups.filter(matchup_number=matchup_number).first()
		return matchup_obj
	
	def get_matchup_obj(self, matchup):
		if isinstance(matchup, TournamentMatchup):
			return TournamentMatchup.objects.filter(id=matchup.id)
		elif isinstance(matchup, (str, int)):
			return StringHelper.get_obj_by_string(TournamentMatchup, matchup)
	
	def get_matchups_by_round_obj(self, round_obj):
		return round_obj.round_matchups.all()
	
	def create_tournament_matchup(self, round_obj, matchup_number):
		matchup = TournamentMatchup.objects.create(
			tournament_round_id=round_obj,
			matchup_number=matchup_number
		)
		matchup_obj = self.get_matchup_obj(matchup)
		return matchup_obj
	
	def update_matchup_competitors(self, matchup_obj, round_competitor):
		matchup_obj.competitors_in_matchup.add(round_competitor)


class LocalTournamentService:

	def __init__(self, 
			base=TournamentBaseService(),
			round=TournamentRoundService(),
			matchup=TournamentMatchupService()
			):
		self.base = base
		self.round = round
		self.matchup = matchup

class APITournamentService:
	pass