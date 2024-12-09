from abc import ABC, abstractmethod
from matchups.models import Matchup
from django.db.models import QuerySet, Q
from typing import List

class MatchupService(ABC):
	
	@abstractmethod
	def create_matchup(self, *args, **kwargs):
		pass

class LocalMatchupService(MatchupService):
	
	def create_matchup(winner_id, loser_id, rating_system, winner_rating_change, loser_rating_change) -> None:
		'''Просто создаю Matchup'''
		matchup = Matchup(
			winner_id = winner_id,
			loser_id = loser_id,
			rating_system = rating_system,
			winner_rating_change = winner_rating_change,
			loser_rating_change = loser_rating_change
		)

	def get_matchups(self, competitor_id) -> QuerySet[Matchup]:
		competitor_matchups = Matchup.objects.filter(
			Q(winner_id=competitor_id) | Q(loser_id=competitor_id))
		return competitor_matchups
	
class APIMatchupService(MatchupService):
	pass