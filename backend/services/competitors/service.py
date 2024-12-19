from django.db.models import Min, Max
from django.db.models import QuerySet
from django.db.models import Q
from abc import ABC, abstractmethod
import random
from typing import List
from apps.competitors.models import Competitor, CompetitorImage

class CompetitorService(ABC):
	
	@abstractmethod
	def get_competitor_object(self, competitor_id):
		pass

	@abstractmethod
	def fetch_competitors(self, competitor_ids):
		pass

	@abstractmethod
	def get_random_competitor(self):
		pass

class LocalCompetitorService(CompetitorService):

	def get_competitor_by_string(self, competitor_id) -> Competitor:
		"""
		Принимает строку с айди компетитора и возвращает объект

		:param competitor_id: str(competitor_id)
		return Competitor
		"""
		competitor = Competitor.objects.get(id=competitor_id)
		return competitor
	
	def get_competitor_object(self, competitor_obj):
		if isinstance(competitor_obj, Competitor):
			return competitor_obj
		elif isinstance(competitor_obj, (str, int)):
			return self.get_competitor_by_string(competitor_obj)
		else:
			print(f'Не вернулся ничего из {competitor_obj}, type{type(competitor_obj)}')
			return None

	def get_random_competitor(self) -> Competitor:
		"""
		Возвращает рандомного компетитора из базы данных
		
		return Competitor 
		"""
		id_range = Competitor.objects.aggregate(
			min_id = Min('id'),
			max_id = Max('id')
		)
		min_id, max_id = id_range['min_id'], id_range['max_id']

		if min_id is None or max_id is None:
			return None
		
		while True:
			random_id = random.randint(min_id, max_id)
			competitor = Competitor.objects.filter(id=random_id).first()
			if competitor:
				return competitor
		
	def get_images(self, competitor_id) -> QuerySet[CompetitorImage]:
		"""
		Возваращает все фото Competitor по строке с id или объекты

		:param competitor_id: Competitor|str(competitor_id)
		return list[CompetitorImage]
		"""
		competitor = self.get_competitor_object(competitor_id)
		competitor_images = competitor.images.all()
		return competitor_images
	
	def get_all_competitors(self):
		return Competitor.objects.all()
	
	def get_competitor_bio(self, competitor_id):
		"""
		По строке с id или объекту Competitor получает CompetitorDetail
		
		:param competitor_id: Competitor|str(competitor_id)
		return CompetitorDetail
		"""
		competitor = self.get_competitor_object(competitor_id)
		return competitor.details.bio
	
	def get_competitors_from_matchups(self, matchups):
		"""
		Возвращает всех Competitor из указанных матчапов

		:param matchups: Matchup
		return list[Competitor]
		"""
		competitors = Competitor.objects.filter(
			Q(id__in=matchups.values_list('winner_id', flat=True)) |
			Q(id__in=matchups.values_list('loser_id', flat=True))
			).distinct()  # distinct удаляет дубликаты
		return competitors
	
	def fetch_competitors(self, competitor_ids) -> QuerySet[Competitor]:
		"""
		По листу с id или объектами

		:param competitor_ids:list[Competitor.id|Competitor]
		возвращаю лист с объектами Competitor
		"""
		competitors = []
		for competitor_id in competitor_ids:
			competitor = self.get_competitor_object(competitor_id)
			competitors.append(competitor)
		return competitors
	
	def fetch_competitors_by_location(self, cities_ids):
		return Competitor.objects.filter(city__id__in=cities_ids)


class APICompetitorService(CompetitorService):
	
	def get_competitor_object(self, competitor_id):
		return Competitor.objects.get(id=competitor_id)

	def fetch_competitors(self, competitor_ids):
		pass
	
	def get_random_competitor(self):
		pass
	
	def get_competitor_data(self, competitor_id):
		competitor = self.get_competitor_object(competitor_id)
		data = {}

		data["name"] = competitor.name
		data["id"] = competitor.id
		data["age"] = competitor.age
		data["city"] = competitor.city.city_eng
		data["bio"] = competitor.details.bio
		if not data["bio"]:
			data["bio"] = '-'
		data["images"] = [{"url": image.get_path()} for image in competitor.images.all()]
		return data
	

