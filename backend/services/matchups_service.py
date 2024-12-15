from django.db import transaction
from django.db.models import QuerySet, Q
from abc import ABC, abstractmethod
from matchups.models import Matchup, SavedMatchup
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
			delta_winner_profile,
			delta_loser_profile,
			profile_id
			
	) -> None:
		'''Просто создаю Matchup'''
		
		matchup = Matchup(
			winner_id=winner_id,
			loser_id=loser_id,
			rating_system=rating_system,
			delta_winner=delta_winner,
			delta_loser=delta_loser,
			delta_winner_profile=delta_winner_profile,
			delta_loser_profile=delta_loser_profile,
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

	@staticmethod
	def create_saved_matchup(profile_id, competitor_1, competitor_2):
		saved_matchup, created = SavedMatchup.objects.get_or_create(
			profile_id=profile_id,
			competitor_1=competitor_1,
			competitor_2=competitor_2
		)
		return saved_matchup
	
	@staticmethod
	def update_saved_matchup(profile_id, competitor_1, competitor_2,
							competitor_1_ii, competitor_2_ii):
		updated_matchup, updated = SavedMatchup.objects.update_or_create(
		defaults={
			'competitor_1': competitor_1,
			'competitor_2': competitor_2,
			'competitor_1_ii': competitor_1_ii,
			'competitor_2_ii': competitor_2_ii,
		}
		)
		return updated_matchup


class APIMatchupService(MatchupService):
	pass
