from django.core.management.base import BaseCommand
from django.db import transaction
from apps.competitors.models import Competitor, CompetitorDetails, CompetitorImage, Location
import os
import json
import csv
from datetime import datetime
import pytz

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

		competitors_id_database = Competitor.objects.values_list('name_id', flat=True)
		persons_to_add = 1
		persons_duplicate = 1

		location_dict = {}
		with open('data/csv/locations.csv', newline='', encoding='utf-8') as f:
			reader = csv.reader(f, delimiter=';')
			for row in reader:
				city_eng = row[0]
				city_ru = row[3]
				country = row[2]
				continent = row[1]
				location_dict[city_eng] = [city_eng, city_ru, country, continent]
		
		check_image_quality = []
		with open('data/csv/image_quality.csv', newline='', encoding='utf-8') as f:
			reader = csv.reader(f)
			for row in reader:
				image = row[0]
				check_image_quality.append(image)

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
					if competitor_data in competitors_id_database:
						persons_duplicate += 1
					else:
						location, created = Location.objects.get_or_create(
							city_eng = location_dict[data[competitor_data]["tinder_city"]][0],
							city_ru = location_dict[data[competitor_data]["tinder_city"]][1],
							country = location_dict[data[competitor_data]["tinder_city"]][2],
							continent = location_dict[data[competitor_data]["tinder_city"]][3],

						)
						competitor = Competitor.objects.create(
							name=data[competitor_data]['name'],
							name_id=competitor_data,
							age=data[competitor_data]['age'],
							city=location
						)
						images_to_add = []
						for image_name in data[competitor_data]["images_by_hashes"]:
							image_full_path = os.path.join('/mnt/g/facemash/images', f"{image_name}.jpg")
							image_local_path = f"{image_name}.jpg"
							if image_local_path not in check_image_quality:
								image_hash = image_name
								beauty_ai_rate = data[competitor_data]["images_by_hashes"][image_name]["beauty_ai"]
								image, recieved = CompetitorImage.objects.get_or_create(
									image_local_path=image_local_path,
									image_hash=image_hash, 
									beauty_ai_rate=beauty_ai_rate,
									image_full_path=image_full_path, 
									)
								images_to_add.append(image)
							else:
								continue
						if images_to_add:
							competitor.images.add(*images_to_add)
						tinder_scrape_time = datetime.strptime(data[competitor_data]["tinder_scrape_time"], "%d-%m-%Y %H:%M:%S")
						local_tz = pytz.timezone('Asia/Bishkek')
						aware_tinder_scrape_time = local_tz.localize(tinder_scrape_time)
						person_detail = CompetitorDetails.objects.create(
							competitor=competitor,
							bio=data[competitor_data]["bio"],
							height=data[competitor_data]["height"],
							work=data[competitor_data]["work"],
							study=data[competitor_data]["study"],
							home=data[competitor_data]["home"],
							looking_for=data[competitor_data]["looking_for"],
							relationship_type=data[competitor_data]["relationship type"],
							pronouns=data[competitor_data]["pronouns"],
							lifestyle=data[competitor_data]["lifestyle"],
							more_about_me=data[competitor_data]["more_about_me"],
							languages=data[competitor_data]["languages"],
							tinder_scrape_time=aware_tinder_scrape_time,
						)
						persons_to_add += 1
		self.stdout.write(self.style.SUCCESS(f'Данные успешно загружены! Добавлено: {persons_to_add}, дубликатов: {persons_duplicate}'))
