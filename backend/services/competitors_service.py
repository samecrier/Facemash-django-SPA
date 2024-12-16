from abc import ABC, abstractmethod
from competitors.models import Competitor, CompetitorImage
from django.db.models import Min, Max
import random
from django.db.models import QuerySet
from typing import List
from django.db.models import Q

class CompetitorService(ABC):
	
	@abstractmethod
	def get_competitor(self, competitor_id):
		pass

	@abstractmethod
	def fetch_competitors(self, competitor_ids):
		pass

	@abstractmethod
	def get_random_competitor(self):
		pass

class LocalCompetitorService(CompetitorService):

	def get_competitor(self, competitor_id) -> Competitor:
		'''
		Принимает competitor_id=str(competitor_id)
		Возвращает Competitor
		'''
		competitor = Competitor.objects.get(id=competitor_id)
		return competitor

	def get_random_competitor(self) -> Competitor:
		'''Возвращает рандомного компетитора из базы данных'''
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
		'''Возваращает все фото Competitor по id'''
		competitor = self.get_competitor(competitor_id)
		competitor_images = competitor.images.all()
		return competitor_images
	
	def fetch_competitors(self, competitor_ids) -> QuerySet[Competitor]:
		'''По листу с id или объектами
		возвращаю лист с объектами Competitor'''
		competitors = []
		for competitor_id in competitor_ids:
			if isinstance(competitor_id, Competitor):
				competitors.append(competitor_id)
			else:
				competitor = Competitor.objects.get(id=competitor_id)
				competitors.append(competitor)
		return competitors
	
	def get_all_competitors(self):
		return Competitor.objects.all()
	
	def get_competitor_bio(self, competitor_obj):
		return competitor_obj.details.bio
	
	def get_competitors_from_matchups(self, matchups):
		competitors = Competitor.objects.filter(
			Q(id__in=matchups.values_list('winner_id', flat=True)) |
			Q(id__in=matchups.values_list('loser_id', flat=True))
			).distinct()  # distinct удаляет дубликаты
		return competitors

	
class APICompetitorService(CompetitorService):
	
	def get_competitor(self, competitor_id):
		return Competitor.objects.get(id=competitor_id)

	def fetch_competitors(self, competitor_ids):
		pass
	
	def get_random_competitor(self):
		pass
	
	def get_competitor_data(self, competitor_id):
		competitor = self.get_competitor(competitor_id)
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


