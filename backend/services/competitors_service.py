from abc import ABC, abstractmethod
from competitors.models import Competitor, CompetitorImage
from django.db.models import Min, Max
import random
from django.db.models import QuerySet
from typing import List

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
		'''Возвращает компетитора по id'''
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

	
class APICompetitorService(CompetitorService):
	
	def get_competitor(self, competitor_id):
		pass

	def fetch_competitors(self, competitor_ids):
		pass
