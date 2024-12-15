from abc import ABC, abstractmethod
from ratings.models import Rating, RatingProfile
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
	def get_top_rating(numbers):
		top_ratings = Rating.objects.order_by('-rating')[:numbers]
		competitors = [(rating.competitor_id, rating.rating) for rating in top_ratings]
		sorted_competitors = sorted(competitors, key=lambda x: (-x[1], x[0].name))
		return sorted_competitors
	
	@staticmethod
	def get_top_ratingprofile(profile_id, numbers):
		top_ratingsprofile = RatingProfile.objects.filter(profile_id=profile_id).order_by('-rating')[:numbers]
		competitors = [(rating.competitor_id, rating.rating) for rating in top_ratingsprofile]
		sorted_competitors = sorted(competitors, key=lambda x: (-x[1], x[0].name))
		return sorted_competitors

	@staticmethod
	def update_matchup_ratingprofile(profile_id, competitor_id, delta, result):
		
		ratingprofile, created = RatingProfile.objects.get_or_create(
			profile_id=profile_id,
			competitor_id=competitor_id
		)

		ratingprofile.rating += delta
		if result == 1:
			ratingprofile.wins += 1
		if result == 0:
			ratingprofile.losses += 1
		ratingprofile.matchups += 1
		ratingprofile.save()


class APIRatingService(RatingService):
	
	def get_rating(self):
		pass
	
	@staticmethod
	def get_top_rating(numbers):
		competitor_service = LocalCompetitorService()
		top_ratings = Rating.objects.order_by('-rating')[:numbers]
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