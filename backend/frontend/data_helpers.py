from __future__ import annotations
from services.competitors_service import LocalCompetitorService
from services.ratings_service import LocalRatingService
from services.profiles_service import LocalProfileService
from services.matchups_service import LocalMatchupService
from django.utils.safestring import mark_safe
import json
from collections import defaultdict
from typing import TYPE_CHECKING, Tuple
from frontend.helpers import Helper

if TYPE_CHECKING:
	from matchups.models import Matchup, SavedMatchup
	from competitors.models import Competitor
	from ratings.models import Rating

class GetData():

	def __init__(self,
		competitor_service=LocalCompetitorService(),
		rating_service = LocalRatingService(),
		profile_service = LocalProfileService(),
		matchup_service = LocalMatchupService(),
		helper_service = Helper(),
	):
		self.competitor_service = competitor_service
		self.rating_service = rating_service
		self.profile_service = profile_service
		self.matchup_service = matchup_service
		self.helper_service = helper_service
	
	def get_data_competitor(self, competitor, initial_index=0):
		data_competitor = {}
		image_data = self.helper_service.get_image_stats(competitor, initial_index=initial_index)
		data_competitor["competitor"] = competitor
		data_competitor["rating"] = self.helper_service.get_rating_stat(competitor)
		data_competitor["images"] = image_data["images"]
		data_competitor["initial_index"] = initial_index
		data_competitor["forloop_index"] = initial_index+1
		return data_competitor

	def get_data_competitors(self, competitors_number) -> dict:
		"""
		Возвращает competitor_number dict для матчапа

		:param competitors_number: int - количество участников
		return dict
		"""
		data = defaultdict(dict)
		competitors = []
		for i in range(competitors_number):
			competitor_number = i+1
			competitor_number_key = f"competitor-{competitor_number}"
			competitor = self.competitor_service.get_random_competitor()
			while True:
				competitor = self.competitor_service.get_random_competitor()
				if competitor not in competitors:
					competitors.append(competitor)
					break
			data_competitor = self.get_data_competitor(competitor)
			data[competitor_number_key] = data_competitor
		data = dict(data)
		return data

	def get_data_enemy(self, winner_id, winner_position, winner_image_index, competitors_number=2) -> dict:
		"""
		По одной строки айди победителя возвращает dict для матчапа
		
		:param winner_id: str(winner_id), 
		:param winner_posiitio: str - позиция победителя на странице,
		:param winner_image_index: str - сохраненный индекс изображения, 
		:param competitors_number: int - возвращаемых участников
		return dict
		"""
		data = defaultdict(dict)
		winner_image_index = int(winner_image_index)
		competitors = []
		winner_competitor = self.competitor_service.get_competitor(winner_id)
		competitors.append(winner_competitor)
		data_competitor = self.get_data_competitor(winner_competitor, winner_image_index)
		data[f"competitor-{winner_position}"] = data_competitor
		
		for i in range(1, competitors_number+1):
			if i != int(winner_position):
				competitor_number = i
				competitor_number_key = f"competitor-{competitor_number}"
				while True:
					competitor = self.competitor_service.get_random_competitor()
					if competitor not in competitors:
						competitors.append(competitor)
						break
				data_competitor = self.get_data_competitor(competitor)
				data[competitor_number_key] = data_competitor
		data = dict(sorted(data.items()))
		return data

	def get_data_saved(self, competitor_1, competitor_2, competitor_1_index=0, competitor_2_index=0) -> dict:
		"""
		По двум объектам Competitor возвращает dict для матчап
		
		:param competitor_1/competitor_2: Competitor
		:param competitor_1_index/competitor_2_index: int - индекс фотографии
		return dict
		"""
		data = defaultdict(dict)
		competitor_1_index = int(competitor_1_index)
		competitor_2_index = int(competitor_2_index)
		data_competitor = self.get_data_competitor(competitor_1, competitor_1_index)
		data["competitor-1"] = data_competitor
		
		data_competitor = self.get_data_competitor(competitor_2, competitor_2_index)
		data["competitor-2"] = data_competitor

		data = dict(sorted(data.items()))
		return data
	
	def get_data_specific_matchup(self, competitor_1, competitor_2, 
						competitor_1_position=1, competitor_1_index=0, 
						competitors_number=2) -> dict:
		"""
		По двум строкам с айди возвращает dict для матчапа

		:param competitor_1/competitor_2: str(Competitor.id), 
		:param competitor_1_position: int - позиция на странице,
		:param competitor_1_index: int - индекс фотографии,
		:param competitors_number: int - количество участников)
		return dict
		"""
		data = defaultdict(dict)
		competitor_1_index = int(competitor_1_index)
		competitor_1 = self.competitor_service.get_competitor(competitor_1)
		data_competitor = self.get_data_competitor(competitor_1, competitor_1_index)
		data[f"competitor-{competitor_1_position}"] = data_competitor

		for i in range(1, competitors_number+1):
			if i != int(competitor_1_position):
				competitor_number = i
				competitor_number_key = f"competitor-{competitor_number}"
				competitor = self.competitor_service.get_competitor(competitor_2)
				data_competitor = self.get_data_competitor(competitor)
				data[competitor_number_key] = data_competitor
		data = dict(sorted(data.items()))
		return data
	
	def get_data_specific_matchup_guest(self, winner_id, winner_position, winner_image_index, 
						enemy_id, competitors_number=2) -> dict:
		'''
		По двум строкам с айди возвращает матчап

		:param winner_id: str(Competitor.id), 
		:param winner_position: str - позиция на странице,
		:param winner_image_index: str - индекс последней фотографии,
		:param enemy_id: str(Competitor.id), 
		:param competitors_number: int - количество участников
		return dict
		'''
		data = defaultdict(dict)
		winner_image_index = int(winner_image_index)
		winner_competitor = self.competitor_service.get_competitor(winner_id)
		data_competitor = self.get_data_competitor(winner_competitor, winner_image_index)
		data[f"competitor-{winner_position}"] = data_competitor
		
		for i in range(1, competitors_number+1):
			if i != int(winner_position):
				competitor_number = i
				competitor_number_key = f"competitor-{competitor_number}"
				competitor = self.competitor_service.get_competitor(enemy_id)
				data_competitor = self.get_data_competitor(competitor, 0)
				data[competitor_number_key] = data_competitor

		data = dict(sorted(data.items()))
		return data
	
	def get_data_competitor_js(self, winner_id, loser_id, winner_position) -> dict:
		"""
		По строкам с айди возвращает дату js формата для обновы на лету

		:param winner_id/loser_id: str(competitor.id),
		:param winner_posiition: str - позиция победителя на странице
		return dict
		"""
		data = defaultdict(lambda: defaultdict(dict))
		winner_obj = self.competitor_service.get_competitor(winner_id)
		loser_obj = self.competitor_service.get_competitor(loser_id)
		for i in range(1, 3):
			if i != int(winner_position):
				competitor_number = i
				competitor_number_key = f"competitor-{competitor_number}"
				competitor = self.competitor_service.get_random_competitor()
				while True:
					competitor = self.competitor_service.get_random_competitor()
					if competitor != winner_obj and competitor != loser_obj:
						data[competitor_number_key]["competitor"]["id"] = competitor.id
						data[competitor_number_key]["competitor"]["name"] = competitor.name
						data[competitor_number_key]["competitor"]["age"] = competitor.age
						data[competitor_number_key]["competitor"]["images"] = [{"url": image.get_path()} for image in competitor.images.all()]
						break
				data[competitor_number_key]["rating"] = self.helper_service.get_rating_stat(competitor)
				data[competitor_number_key]["winner_id"] = competitor.id
				data[competitor_number_key]["winner_position"] = i
				data[competitor_number_key]["loser_id"] = winner_id
				data[competitor_number_key]["initial_index"] = 0
				data[competitor_number_key]["forloop_index"] = 1
		data = dict(data)
		return data