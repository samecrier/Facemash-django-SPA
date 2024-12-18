from __future__ import annotations
from services.competitors.service import LocalCompetitorService
from services.ratings.service import LocalRatingService
from services.profiles.service import LocalProfileService
from services.matchups.service import LocalMatchupService
from services.matchups.data_helper import DataHelper
from django.utils.safestring import mark_safe
import json
from collections import defaultdict
from typing import TYPE_CHECKING, Tuple
from services.helpers import Helper
from services.matchups.helper import MatchupHelper

if TYPE_CHECKING:
	from apps.matchups.models import Matchup, SavedMatchup
	from apps.competitors.models import Competitor
	from apps.ratings.models import Rating

class MatchupGetData():

	def __init__(self,
		competitor_service=LocalCompetitorService(),
		rating_service=LocalRatingService(),
		profile_service=LocalProfileService(),
		matchup_service=LocalMatchupService(),
		matchup_helper_service=MatchupHelper(),
	):
		self.competitor_service = competitor_service
		self.rating_service = rating_service
		self.profile_service = profile_service
		self.matchup_service = matchup_service
		self.matchup_helper_service = matchup_helper_service
	
	def get_data_competitor(self, competitor, initial_index=0):
		"""
		Возвращает данные компетитора в нужной форме

		:param competitor: Competitor
		:param initial_index: int - индекс первой фотографии
		return dict
		"""
		data_competitor = {}
		competitor = self.competitor_service.get_competitor_object(competitor)
		image_data = Helper.get_image_stats(competitor, initial_index=initial_index)
		data_competitor["competitor"] = competitor
		data_competitor["rating"] = self.matchup_helper_service.get_rating_stat(competitor)
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

	def data_matchup(self, competitors=None, **kwargs):
		
		raw_data = DataHelper.dict_from_params(kwargs)
		template_data = {}
		for key in raw_data:
			local_data = DataHelper.generate_params_matchup(raw_data[key])
			template_data[key] = local_data
		data_for_matchup = DataHelper.get_data_matchup(template_data)
		
		final_data = {}
		for competitor in data_for_matchup:
			data_competitor = self.get_data_competitor(data_for_matchup[competitor]['id'], data_for_matchup[competitor]['index'])
			final_data[competitor] = data_competitor

		if competitors:
			need_competitors = competitors-len(raw_data)
			for i in range(need_competitors):
				final_data.update(self.get_data_random_competitors(
					competitors_number=need_competitors, 
					first_position=len(raw_data)))

		competitor_final_data = {f"competitor-{key}": value for key, value in sorted(final_data.items())}

		return competitor_final_data
	
class MatchupGetDataJS():

	def __init__(
			self,
			competitor_service=LocalCompetitorService(),
			matchup_helper_service=MatchupHelper()
	):
		self.competitor_service = competitor_service
		self.matchup_helper_service = matchup_helper_service

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
				data[competitor_number_key]["rating"] = self.matchup_helper_service.get_rating_stat(competitor)
				data[competitor_number_key]["winner_id"] = competitor.id
				data[competitor_number_key]["winner_position"] = i
				data[competitor_number_key]["loser_id"] = winner_id
				data[competitor_number_key]["initial_index"] = 0
				data[competitor_number_key]["forloop_index"] = 1
		data = dict(data)
		return data