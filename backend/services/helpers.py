from __future__ import annotations
from services.competitors.service import LocalCompetitorService
from services.ratings.service import LocalRatingService
from services.profiles.service import LocalProfileService
from services.matchups.service import LocalMatchupService
from django.utils.safestring import mark_safe
from django.apps import apps
from collections import defaultdict
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
	
	@staticmethod
	def convert_to_dict(obj):
		if isinstance(obj, defaultdict):
			# Преобразуем defaultdict в обычный словарь
			return {key: Helper.convert_to_dict(value) for key, value in obj.items()}
		elif isinstance(obj, dict):
			# Рекурсивно обрабатываем словари
			return {key: Helper.convert_to_dict(value) for key, value in obj.items()}
		elif isinstance(obj, list):
			# Рекурсивно обрабатываем списки
			return [Helper.convert_to_dict(item) for item in obj]
		else:
			# Возвращаем неизмененные объекты
			return obj


	@staticmethod
	def get_model_object(app, model):
		"""Возвращает объект модели для проверки в ifinstance без импорта
		User = get_model_object('apps.profiles', 'User')
		Вместо import User
		"""

		model = apps.get_model(app, model)
		return model