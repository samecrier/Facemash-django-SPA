from __future__ import annotations
from service.competitors.service import LocalCompetitorService
from service.ratings.service import LocalRatingService
from service.profiles.service import LocalProfileService
from service.matchups.service import LocalMatchupService
from django.utils.safestring import mark_safe
import json
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from apps.matchups.models import Matchup, SavedMatchup
	from apps.competitors.models import Competitor
	from apps.ratings.models import Rating

class Helper():
	
	@staticmethod
	def get_image_stats(competitor, initial_index=0) -> dict:
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