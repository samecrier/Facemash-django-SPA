from service.competitors.service import LocalCompetitorService
from service.matchups.service import LocalMatchupService
from service.ratings.service import LocalRatingService
from service.helpers import Helper


class CompetitorGetData():
	
	def __init__(
			self,
			competitor_service=LocalCompetitorService(),
		):
		self.competitor_service = competitor_service

	def get_competitor_profile(self, competitor_id) -> dict:
		"""
		По строке с айди возвращает данные для компетитор профайла

		:param competitor_id: str(competitor.id)
		return dict
		"""
		competitor_obj = self.competitor_service.get_competitor_object(competitor_id)
		data = {}
		data["name"] = competitor_obj.name
		data["id"] = competitor_obj.id
		data["age"] = competitor_obj.age
		data["city"] = competitor_obj.city.city_eng
		image_data = Helper.get_image_stats(competitor_obj)
		data["rating"] = LocalRatingService.get_rating(competitor_obj)
		data["images"] = image_data["images"]
		data["bio"] = self.competitor_service.get_competitor_bio(competitor_obj)
		if not data["bio"]:
			data["bio"] = '-'
		data["matchups"] = LocalMatchupService.get_competitor_matchups(competitor_id)
		return data

