from __future__ import annotations
import logging
from services.competitors.service import LocalCompetitorService
from services.ratings.service import LocalRatingService
from services.profiles.service import LocalProfileService
from services.matchups.service import LocalMatchupService
from django.utils.safestring import mark_safe
from django.apps import apps
from collections import defaultdict
from django.db import connection
from functools import wraps
import time
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
	

def debug_queries(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		queries_before = len(connection.queries)
		result = func(*args, **kwargs)
		queries_after = len(connection.queries)
		print(f"Function {func.__name__} executed {queries_after - queries_before} SQL queries")
		return result
	return wrapper

logger = logging.getLogger(__name__)

def measure_time(func):
	"""
	Декоратор для измерения времени выполнения функции.
	"""
	def wrapper(*args, **kwargs):
		start_time = time.perf_counter()  # Начало замера времени
		result = func(*args, **kwargs)   # Выполнение функции
		end_time = time.perf_counter()   # Конец замера времени
		elapsed_time = end_time - start_time
		logger.info(f"Время выполнения {func.__name__}: {elapsed_time:.4f} секунд")
		print(f"Время выполнения {func.__name__}: {elapsed_time:.4f} секунд")
		return result
	return wrapper