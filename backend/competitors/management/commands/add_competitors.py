from django.core.management.base import BaseCommand
from django.db import transaction
from competitors.models import Competitor, CompetitorDetails, CompetitorImage, Location
import os
import json
import csv

class Command(BaseCommand):
	help = 'Загрузка компетиторов из JSON'

	def add_arguments(self, parser):
		parser.add_argument('--path', type=str, help='Путь к JSON файлу')

	def handle(self, *args, **kwargs):
		file_pathes = []
		if kwargs['path']:
			file_path = f"data/json/{kwargs['option']}"
			file_pathes.append(file_path)
		else:
			root_path = 'data/json'
			for filename in os.listdir(root_path):
				file_pathes.append(os.path.join(root_path, filename))

		# competitors_id_database = Competitor.objects.values_list('name_id', flat=True)
		persons_to_add = 0
		persons_duplicate = 0

		location_dict = {}
		with open('data/csv/locations.csv', newline='', encoding='utf-8-sig') as f:
			reader = csv.reader(f, delimiter=';')
			for row in reader:
				city_eng = row[0]
				city_ru = row[3]
				country = row[2]
				continent = row[1]
				location_dict[city_eng] = [city_eng, city_ru, country, continent]
		
		with transaction.atomic():
			for i, file_path in enumerate(file_pathes):
				try:
					with open(file_path, 'r', encoding='utf-8') as f:
						data = json.load(f)
				except Exception as e:
					data = None
					print(f'Не удалось открыть json {e}')
					continue
				for competitor_data in data:
					if persons_to_add % 10000 == 0:
						print(f'Добавлено {persons_to_add}')
					print(competitor_data)
					# if competitor_data not in competitors_id_database:
					# 	pass
