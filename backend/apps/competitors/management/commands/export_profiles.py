import json
import os
from django.core.management.base import BaseCommand
from apps.competitors.models import Competitor
import shutil

class Command(BaseCommand):
	help = "Export competitors data to JSON"

	def add_arguments(self, parser):
		parser.add_argument(
			'--cities',
			type=str,
			nargs='+',
			help='City:qty format'
		)

	def copy_images(self, competitor):
		images_list = []
		destination_folder = '/mnt/g/facemash/new_base/images/'
		
		for img in competitor.images.all():
			original_path = img.image_full_path
			new_path = os.path.join(destination_folder, img.image_local_path)
			shutil.copy(original_path, new_path)
			images_list.append(img.image_hash)
		return images_list
	
	def handle(self, *args, **options):
		cities = options['cities']
		final_set = []
		queryset = Competitor.objects.select_related(
			"city",          # ForeignKey(Location)
			"details"        # OneToOneField(CompetitorDetails)
		).prefetch_related(
			"images"         # ManyToManyField(CompetitorImage)
		)
		for city in cities:
			city_split = city.split(':')
			city = city_split[0]
			qty = int(city_split[1])
			filtered_set = queryset.filter(city__city_eng=city).order_by('?')[:qty]
			final_set.extend(list(filtered_set))

		data = [
			{
				"competitor_name": competitor.name,
				"competitor_name_id": competitor.name_id,
				"competitor_age": competitor.age,
				"location_city_eng": competitor.city.city_eng,
				"location_city_ru": competitor.city.city_ru,
				"location_country": competitor.city.country,
				"location_continent": competitor.city.continent,
				"image_hashes": self.copy_images(competitor),
				"competitordetails_bio": competitor.details.bio,
				"competitordetails_height": competitor.details.height,
				"competitordetails_work": competitor.details.work,
				"competitordetails_study": competitor.details.study,
				"competitordetails_home": competitor.details.home,
				"competitordetails_looking_for": competitor.details.looking_for,
				"competitordetails_relationship_type": competitor.details.relationship_type,
				"competitordetails_pronouns": competitor.details.pronouns,
				"competitordetails_lifestyle": competitor.details.lifestyle,
				"competitordetails_more_about_me": competitor.details.more_about_me,
				"competitordetails_languages": competitor.details.languages,
				"competitordetails_tinder_scrape_time": competitor.details.tinder_scrape_time.isoformat(),

			}
			for competitor in final_set
		]

		output_dir = os.path.join("data")
		os.makedirs(output_dir, exist_ok=True)

		file_path = os.path.join(output_dir, "/mnt/g/facemash/new_base/exported_profiles.json")
		with open(file_path, "w", encoding="utf-8") as f:
			json.dump(data, f, indent=4, ensure_ascii=False)

		self.stdout.write(self.style.SUCCESS(f"Exported {len(data)} profiles to {file_path}"))
