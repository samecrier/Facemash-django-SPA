from abc import ABC, abstractmethod
from ratings.models import Rating
from ratings_system import EloRatingSystem
from competitors_service import LocalCompetitorService
from typing import List

class RatingService(ABC):
	@abstractmethod
	def get_rating(self, competitor_id):
		pass


class LocalRatingService(RatingService):
	
	@staticmethod
	def get_rating(competitor_id) -> int:
		'''По id Competitor возвращаю его рейтинг'''
		competitor_rating = Rating.objects.get(competitor_id=competitor_id)
		return competitor_rating.rating
	
	@staticmethod
	def update_rating(competitor_id, rating, cost) -> None:
		'''
		Функции принимает id Competitor, текущий рейтинг
		elo cost и обновляет рейтинг.
		'''
		competitor_rating = Rating.objects.get(competitor_id=competitor_id)
		competitor_rating.rating = rating+cost
		competitor_rating.save()
	
class APIRatingService(RatingService):
	pass