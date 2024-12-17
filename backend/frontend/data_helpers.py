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
		rating_service=LocalRatingService(),
		profile_service=LocalProfileService(),
		matchup_service=LocalMatchupService(),
		helper_service=Helper(),
	):
		self.competitor_service = competitor_service
		self.rating_service = rating_service
		self.profile_service = profile_service
		self.matchup_service = matchup_service
		self.helper_service = helper_service
	
	def get_data_competitor(self, competitor, initial_index=0):
		"""
		Возвращает данные компетитора в нужной форме

		:param competitor: Competitor
		:param initial_index: int - индекс первой фотографии
		return dict
		"""
		data_competitor = {}
		competitor = self.competitor_service.get_competitor_object(competitor)
		image_data = self.helper_service.get_image_stats(competitor, initial_index=initial_index)
		data_competitor["competitor"] = competitor
		data_competitor["rating"] = self.helper_service.get_rating_stat(competitor)
		data_competitor["images"] = image_data["images"]
		data_competitor["initial_index"] = initial_index
		data_competitor["forloop_index"] = initial_index+1

		return data_competitor

	def get_data_random_competitors(self, competitors_number, first_position=0) -> dict:
		"""
		Возвращает competitor_number dict для матчапа

		:param competitors_number: int - количество участников
		return dict
		"""
		data = defaultdict(dict)
		start_position = first_position + 1
		finish_position = start_position + competitors_number
		competitors = []
		for i_competitor in range(start_position, finish_position):
			competitor_number_key = f"competitor-{i_competitor}"
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
		winner_competitor = self.competitor_service.get_competitor_object(winner_id)
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
	
	def get_data_specific_matchup(self, competitor_1, competitor_2, 
						competitor_1_index=0, competitor_2_index=0, 
						competitor_1_position=1, competitors_number=2) -> dict:
		"""
		По двум строкам с айди возвращает dict для матчапа. Параметр competitor_1
		может изменять свою позицию на экране и использоваться как 
		winner_id + winner_positon + winner_image_index

		:param competitor_1/competitor_2: str(Competitor.id), 
		:param competitor_1_position: int - позиция на странице,
		:param competitor_1_index: int - индекс фотографии,
		:param competitors_number: int - количество участников)
		return dict
		"""

		data = defaultdict(dict)
		competitor_1_index = int(competitor_1_index)
		competitor_1 = self.competitor_service.get_competitor_object(competitor_1)
		data_competitor = self.get_data_competitor(competitor_1, competitor_1_index)
		data[f"competitor-{competitor_1_position}"] = data_competitor

		for i in range(1, competitors_number+1):
			if i != int(competitor_1_position):
				competitor_number = i
				competitor_number_key = f"competitor-{competitor_number}"
				competitor = self.competitor_service.get_competitor_object(competitor_2)
				data_competitor = self.get_data_competitor(competitor, competitor_2_index)
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
		winner_obj = self.competitor_service.get_competitor_object(winner_id)
		loser_obj = self.competitor_service.get_competitor_object(loser_id)
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
	
	def get_data_matchup(self, *args, **kwargs):
		data = defaultdict(dict)
		position_slots = [kwargs[key]['position'] for key in kwargs]
		filtered_positions = [pos for pos in position_slots if pos is not None]
		if len(filtered_positions) != len(set(filtered_positions)):
			raise ValueError(f"Ошибка: имеются повторяющиеся позиции {filtered_positions}")
		range_position = [i for i in range(1, len(kwargs)+1)]
		for i_competitor in kwargs:

			if kwargs[i_competitor]['position']:
				if kwargs[i_competitor]['position'] > len(kwargs):
					raise ValueError(f"{i_competitor} имеет позицию {kwargs[i_competitor]['position']}, что превышает длину {len(kwargs)}")
				position = kwargs[i_competitor]['position']
			else:
				for position_index in range_position:
					if position_index not in filtered_positions:
						none_index = position_slots.index(None)
						position = position_index
						position_slots[none_index] = position_index
						filtered_positions.append(position_index)
						break
			
			if not kwargs[i_competitor]['id']:
				raise ValueError(f"Ошибка: передался id=None для competitor-{i_competitor}")
			data[position]['id'] = kwargs[i_competitor]['id']
			if kwargs[i_competitor]['index']:
				data[position]['index'] = kwargs[i_competitor]['index']
			else:
				data[position]['index'] = 0
		
		data = dict(data)
		return data

	def generate_params_matchup(self, *args, **kwargs):
		data = {
			'id': None,
			'index': None,
			'position': None
		}
		for key, value in kwargs.items():
			data[key] = value
		return data


	def dict_from_params(self, data):
		result = {}
		for key, value in data.items():
			try:
				parts = key.rsplit("_", 1)  # Разделить на две части, начиная с конца
				main_key, sub_key = parts[0], parts[1]
				
				# Вложенный словарь с ключом main_key
				if main_key not in result:
					result[main_key] = {}
				
				if isinstance(value, (str, int)):
					result[main_key][sub_key] = int(value)
				else:
					result[main_key][sub_key] = value
			except IndexError:
				pass
		return result

	def matchup(self, *args, **kwargs):

		raw_data = self.dict_from_params(kwargs)
		data = {}
		for i, key in enumerate(raw_data):
			i_competitor = str(i+1)
			local_data = self.generate_params_matchup(**raw_data[key])
			data[key] = local_data
		data_for_matchup = self.get_data_matchup(**data)
		
		final_data = {}
		for competitor in data_for_matchup:
			data_competitor = self.get_data_competitor(data_for_matchup[competitor]['id'], data_for_matchup[competitor]['index'])
			final_data[competitor] = data_competitor

		competitors = kwargs.get('competitors') 
		if competitors:
			need_competitors = competitors-len(raw_data)
			for i in range(need_competitors):
				final_data.update(self.get_data_random_competitors(
					competitors_number=need_competitors, 
					first_position=len(raw_data)))

		competitor_final_data = {f"competitor-{key}": value for key, value in sorted(final_data.items())}

		
		return competitor_final_data