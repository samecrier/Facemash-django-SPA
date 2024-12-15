from django.db import transaction
from django.db.models import QuerySet, Q
from abc import ABC, abstractmethod
from matchups.models import Matchup
from typing import List


class MatchupService(ABC):

	@abstractmethod
	def create_matchup(self, *args, **kwargs):
		pass


class LocalMatchupService(MatchupService):
	
	@transaction.atomic
	def create_matchup(
			self, winner_id, loser_id,
			rating_system,
			delta_winner, delta_loser,
			profile_id
			
	) -> None:
		'''Просто создаю Matchup'''
		
		matchup = Matchup(
			winner_id=winner_id,
			loser_id=loser_id,
			rating_system=rating_system,
			delta_winner=delta_winner,
			delta_loser=delta_loser,
			profile_id=profile_id
		)
		matchup.save()
	def get_matchups(self, competitor_id) -> QuerySet[Matchup]:
		'''Возвращает все матчапы по competitor_id'''
		competitor_matchups = Matchup.objects.filter(
			Q(winner_id=competitor_id) | Q(loser_id=competitor_id))
		return competitor_matchups

	@staticmethod
	def update_profile_with_guest(profile_obj, guest_profile):
		Matchup.objects.filter(profile_id=profile_obj).update(profile_id=guest_profile)


class APIMatchupService(MatchupService):
	pass
