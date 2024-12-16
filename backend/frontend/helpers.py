from __future__ import annotations
from services.competitors_service import LocalCompetitorService
from services.ratings_service import LocalRatingService
from services.profiles_service import LocalProfileService
from services.matchups_service import LocalMatchupService
from django.utils.safestring import mark_safe
import json
from collections import defaultdict
from typing import TYPE_CHECKING, Tuple
if TYPE_CHECKING:
	from matchups.models import Matchup, SavedMatchup
	from competitors.models import Competitor
	from ratings.models import Rating

class Helper():
	
	def __init__(self,
		competitor_service=LocalCompetitorService(),
		rating_service = LocalRatingService(),
		profile_service = LocalProfileService(),
		matchup_service = LocalMatchupService(),
	):
		self.competitor_service = competitor_service
		self.rating_service = rating_service
		self.profile_service = profile_service
		self.matchup_service = matchup_service

	def get_rating_stat(self, competitor) -> int :
		"""
		Возвращает рейтинг объекта Competitor

		:param competitor: Competitor 
		return Rating.rating
		"""

		return self.rating_service.get_rating(competitor)
		
	def get_image_stats(self, competitor, initial_index=0) -> dict:
		"""
		Возвращает dict с различными image ключами

		:param competitor: Competitor, 
		:param initial_index: int - первое изображение
		return dict
		"""
		images = [image.get_path() for image in competitor.images.all()]
		initial_index = int(initial_index)
		initial_image = images[initial_index]
		image_count = len(images)
		other_images = mark_safe(json.dumps(images))
		images = mark_safe(json.dumps(images))
		# print(f"first{initial_image}, {images}")
		return {
			"images": images, "initial_image":initial_image, 
			"other_images":other_images, "image_count":image_count
		}
	
	def get_winner_rating(self, winner_id) -> int:
		"""
		По строке с айди возвращает рейтинг компетитора

		:param winner_id:Competitor|str(competitor.id)
		return Rating.rating
		"""
		return self.rating_service.get_rating(winner_id)
	
	def get_competitor_profile(self, competitor_id) -> dict:
		"""
		По строке с айди возвращает данные для компетитор профайла

		:param competitor_id: str(competitor.id)
		return dict
		"""
		competitor_obj = self.competitor_service.get_competitor(competitor_id)
		data = {}
		data["name"] = competitor_obj.name
		data["id"] = competitor_obj.id
		data["age"] = competitor_obj.age
		data["city"] = competitor_obj.city.city_eng
		image_data = self.get_image_stats(competitor_obj)
		data["rating"] = self.rating_service.get_rating(competitor_obj)
		data["images"] = image_data["images"]
		data["bio"] = self.competitor_service.get_competitor_bio(competitor_obj)
		if not data["bio"]:
			data["bio"] = '-'
		data["matchups"] = self.matchup_service.get_competitor_matchups(competitor_id)
		return data
	
	def get_saved_matchup(self, request) -> SavedMatchup:
		"""
		Получает или создает сохраненный матчап

		:param request: request
		return SavedMatchup|False
		"""
		if request.user.is_authenticated:
			try:
				saved_matchup = request.user.saved_matchup
				return saved_matchup
			except:
				competitor_1 = self.competitor_service.get_random_competitor()
				while True:
					competitor_2 = self.competitor_service.get_random_competitor()
					if competitor_2 != competitor_1:
						saved_matchup = self.matchup_service.create_saved_matchup(
							request.user, competitor_1, competitor_2)
						return saved_matchup
				
		else:
			return False

	def update_saved_matchup(self, profile_id, winner_id, winner_position,
		winner_image_index, enemy_id) -> SavedMatchup:
		"""
		Обновляет последний сохраненный матчап и получает этот объект

		:param profile_id: Profile, 
		:param winner_id/enemy_id: str(Competitor.id)
		:param winner_position: int - позиция на странице
		:param winner_image_index: int -индекс фотографии
		return SavedMatchup
		"""
		winner_id = self.competitor_service.get_competitor(winner_id)
		enemy_id = self.competitor_service.get_competitor(enemy_id)
		if winner_position == '1':
			updated_matchup = self.matchup_service.update_saved_matchup(
				profile_id=profile_id, 
				competitor_1=winner_id,
				competitor_2=enemy_id,
				competitor_1_ii=winner_image_index,
				competitor_2_ii=0
			)
		else:
			updated_matchup = self.matchup_service.update_saved_matchup(
				profile_id=profile_id, 
				competitor_1=enemy_id,
				competitor_2=winner_id,
				competitor_1_ii=0,
				competitor_2_ii=winner_image_index
			)
		return updated_matchup
	
	def get_two_competitors(self) -> Tuple[Competitor, Competitor]:
		"""
		Возвращает два рандомных компетитора
		return (Competitor, Competitor)
		"""
		competitor_1 = self.competitor_service.get_random_competitor()
		while True:
			competitor_2 = self.competitor_service.get_random_competitor()
			if competitor_2 != competitor_1:
				break
		return (competitor_1, competitor_2)
	
	def get_profile_matchups(self, profile_id, number=None):
		"""
		Получает number количество матчапов для профиля

		:param profile_id: Profile
		:param number: int - количество матчапов
		return dict
		"""
		matchups = self.matchup_service.get_profile_matchups(profile_id).order_by('-created_at')
		if number:
			matchups = matchups[:number]
	
		competitor_ids = self.competitor_service.get_competitors_from_matchups(matchups)
		ratings = self.rating_service.get_rating_profiles(profile_id, competitor_ids)
		
		data = defaultdict(dict)
		for i, matchup in enumerate(matchups):
			i = i+1
			data[i]["winner"] = matchup.winner_id
			data[i]["loser"] = matchup.loser_id
			data[i]["winner_rating"] = ratings[matchup.winner_id]
			data[i]["loser_rating"] = ratings[matchup.loser_id]
			data[i]["delta_winner"] = matchup.delta_winner_profile
			data[i]["delta_loser"] = matchup.delta_loser_profile
			ratings[matchup.winner_id] -= matchup.delta_winner_profile
			ratings[matchup.loser_id] += matchup.delta_loser_profile
		data = dict(data)
		return data