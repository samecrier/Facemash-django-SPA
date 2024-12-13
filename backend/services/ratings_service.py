from abc import ABC, abstractmethod
from ratings.models import Rating
from services.ratings_system import EloRatingSystem
from services.competitors_service import LocalCompetitorService
from typing import List

class RatingService(ABC):
	@abstractmethod
	def get_rating(self, competitor_id):
		pass


class LocalRatingService(RatingService):
	
	@staticmethod
	def get_rating(competitor) -> int:
		'''По id Competitor возвращаю его рейтинг'''
		competitor_rating = Rating.objects.get(competitor_id=competitor)
		return competitor_rating.rating
	
	@staticmethod
	def update_matchup_rating(competitor_id, delta, result) -> None:
		'''
		Функции принимает id Competitor, текущий рейтинг
		elo delta и обновляет рейтинг.
		'''
		competitor_rating = Rating.objects.get(competitor_id=competitor_id)
		competitor_rating.rating = competitor_rating.rating+delta
		if result == 1:
			competitor_rating.wins += 1
		if result == 0:
			competitor_rating.losses += 1
		competitor_rating.matchups += 1
		competitor_rating.save()
	
	def create_competitor_rating(self, competitor):
		if Rating.objects.filter(competitor_id=competitor).exists():
			return False
		Rating.objects.create(
			competitor_id=competitor
		)
		return True
	
	@staticmethod
	def get_top_rating():
		competitor_service = LocalCompetitorService()
		top_ratings = Rating.objects.order_by('-rating')[:20]
		competitors = [(rating.competitor_id, rating.rating) for rating in top_ratings]
		# competitor_service.fetch_competitors(competitors)
		return competitors
	


class APIRatingService(RatingService):
	
	def get_rating(self):
		pass
	
	@staticmethod
	def get_top_rating():
		competitor_service = LocalCompetitorService()
		top_ratings = Rating.objects.order_by('-rating')[:20]
		competitors = [(rating.competitor_id, rating.rating) for rating in top_ratings]
		data = []
		for competitor, rating in competitors:
			data_competitor = {}
			data_competitor["name"] = competitor.name_id
			data_competitor["id"] = competitor.id
			data_competitor["city"] = competitor.city.city_eng
			data_competitor["rating"] = rating
			data.append(data_competitor)
			

		# competitor_service.fetch_competitors(competitors)
		return data