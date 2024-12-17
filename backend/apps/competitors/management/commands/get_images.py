from django.core.management.base import BaseCommand
from django.db import transaction
import json
import csv
from apps.competitors.models import Competitor, CompetitorImage
import os

class Command(BaseCommand):
	help = 'Загрузить изображения для существующих Competitor'

	def handle(self, *args, **kwargs):
		with open('data/json/full.json', 'r', encoding='utf-8') as f:
			data = json.load(f)
			
		res_data = []
		with open('data/csv/resolution.csv', 'r', newline='', encoding='utf-8') as f:
			reader = csv.reader(f)
			for row in reader:
				res_data.append(*row)
		process = len(res_data)
		added_images = []
		with transaction.atomic():
			for hash_image in res_data:
				for user in data:
					if hash_image in data[user]["images_by_hashes"]:
						competitor = Competitor.objects.get(name_id=user)
						image_full_path = os.path.join('/mnt/g/facemash/images', f"{hash_image}.jpg")
						image_local_path = f"{hash_image}.jpg"
						image_hash = hash_image
						beauty_ai_rate = data[user]["images_by_hashes"][hash_image]["beauty_ai"]
						image, recieved = CompetitorImage.objects.get_or_create(
							image_local_path=image_local_path,
							image_hash=image_hash, 
							beauty_ai_rate=beauty_ai_rate,
							image_full_path=image_full_path, 
							)
						if image:
							print(user, image)
							added_images.append(image)
							competitor.images.add(image)
		with open('data/csv/added_images.csv', 'a', newline='', encoding='utf-8') as f:
			writer = csv.writer(f)
			for row in added_images:
				if isinstance(row, list):
					pass
				else:
					row = [row]
				writer.writerow(row)
		
		self.stdout.write(self.style.SUCCESS(f'Данные успешно загружены!'))
