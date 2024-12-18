from django.core.management.base import BaseCommand
from django.db import transaction
from services.competitors.service import LocalCompetitorService
from services.ratings.service import LocalRatingService

class Command(BaseCommand):
	help = 'Добавить рейтинг для все компетиторов'

	def handle(self, *args, **kwargs):
		competitor_service = LocalCompetitorService()
		rating_service = LocalRatingService()
		duplicates = 0
		added_accounts = 0
		with transaction.atomic():
			competitors = competitor_service.get_all_competitors()
			len_competitors = len(competitors)
			for i, competitor in enumerate(competitors):
				print(i, len_competitors)
				result = rating_service.create_competitor_rating(competitor)
				if result:
					# print(f"Добавил {competitor.name_id}")
					added_accounts += 1
				else:
					duplicates += 1
					# print(f"Дубликат {competitor.name_id}")
					pass
		self.stdout.write(self.style.SUCCESS
			(f'Новых аккаунтов: {added_accounts}, дубликатов: {duplicates}')
		)