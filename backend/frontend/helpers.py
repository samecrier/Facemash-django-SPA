from services.competitors_service import LocalCompetitorService
from services.ratings_service import LocalRatingService
from django.utils.safestring import mark_safe
import json
from collections import defaultdict

class GetData():
	competitor_service = LocalCompetitorService()
	rating_service = LocalRatingService()

	def get_rating_stat(self, competitor):
		return self.rating_service.get_rating(competitor)
		

	def get_image_stats(self, competitor, initial_index=0) -> list:
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
	
	def get_data_competitors(self, competitors_number) -> dict:
		data = defaultdict(dict)
		competitors = []
		for i in range(competitors_number):
			competitor_number = i+1
			competitor_number_key = f"competitor-{competitor_number}"
			competitor = self.competitor_service.get_random_competitor()
			while True:
				competitor = self.competitor_service.get_random_competitor()
				if competitor not in competitors:
					data[competitor_number_key]["competitor"] = competitor
					competitors.append(competitor)
					break
			data[competitor_number_key]["rating"] = self.get_rating_stat(competitor)
			image_data = self.get_image_stats(competitor)
			data[competitor_number_key]["images"] = image_data["images"]
			data[competitor_number_key]["initial_index"] = 0
			data[competitor_number_key]["forloop_index"] = 1
		data = dict(data)
		return data
	
	def get_enemy(self, winner_id, winner_position, winner_image_index, competitors_number=2) -> dict:
		data = defaultdict(dict)
		winner_image_index = int(winner_image_index)
		competitors = []
		winner_competitor = self.competitor_service.get_competitor(winner_id)
		competitors.append(winner_competitor)
		image_data = self.get_image_stats(winner_competitor, initial_index=winner_image_index)
		data[f"competitor-{winner_position}"]["competitor"] = winner_competitor
		data[f"competitor-{winner_position}"]["rating"] = self.get_rating_stat(winner_competitor)
		data[f"competitor-{winner_position}"]["images"] = image_data["images"]
		data[f"competitor-{winner_position}"]["initial_index"] = winner_image_index
		data[f"competitor-{winner_position}"]["forloop_index"] = winner_image_index+1
		
		for i in range(1, competitors_number+1):
			if i != int(winner_position):
				competitor_number = i
				competitor_number_key = f"competitor-{competitor_number}"
				while True:
					competitor = self.competitor_service.get_random_competitor()
					if competitor not in competitors:
						data[competitor_number_key]["competitor"] = competitor
						competitors.append(competitor)
						break
				image_data = self.get_image_stats(competitor)
				data[competitor_number_key]["rating"] = self.get_rating_stat(competitor)
				data[competitor_number_key]["images"] = image_data["images"]
				data[competitor_number_key]["initial_index"] = 0
				data[competitor_number_key]["forloop_index"] = 1
		data = dict(sorted(data.items()))
		return data
	
	def get_competitor_js(self, winner_id, loser_id, winner_position):
		data = defaultdict(lambda: defaultdict(dict))
		winner_obj = self.competitor_service.get_competitor(winner_id)
		loser_obj = self.competitor_service.get_competitor(loser_id)
		for i in range(1, 3):
			if i != int(winner_position):
				competitor_number = i
				competitor_number_key = f"competitor-{competitor_number}"
				competitor = self.competitor_service.get_random_competitor()
				while True:
					competitor = self.competitor_service.get_random_competitor()
					if competitor != winner_obj and competitor != loser_obj:
						data[competitor_number_key]["competitor"]["id"] = competitor.id
						data[competitor_number_key]["competitor"]["name"] = competitor.name_id
						data[competitor_number_key]["competitor"]["age"] = competitor.age
						data[competitor_number_key]["competitor"]["images"] = [{"url": image.get_path()} for image in competitor.images.all()]
						break
				data[competitor_number_key]["rating"] = self.get_rating_stat(competitor)
				data[competitor_number_key]["winner_id"] = competitor.id
				data[competitor_number_key]["winner_position"] = i
				data[competitor_number_key]["loser_id"] = winner_id
				data[competitor_number_key]["initial_index"] = 0
				data[competitor_number_key]["forloop_index"] = 1
		data = dict(data)
		return data
	
	def get_winner_rating(self, winner_id):
		return self.rating_service.get_rating(winner_id)
	
	def get_competitor_profile(self, competitor_id):
		competitor_obj = self.competitor_service.get_competitor(competitor_id)
		data = {}
		data["name"] = competitor_obj.name
		data["age"] = competitor_obj.age
		data["city"] = competitor_obj.city.city_eng
		image_data = self.get_image_stats(competitor_obj)
		data["images"] = image_data["images"]
		data["bio"] = self.competitor_service.get_competitor_bio(competitor_obj)
		return data

	def get_specific_matchup(self, winner_id, winner_position, winner_image_index, 
						enemy_id, competitors_number=2):
		data = defaultdict(dict)
		winner_image_index = int(winner_image_index)
		competitors = []
		winner_competitor = self.competitor_service.get_competitor(winner_id)
		competitors.append(winner_competitor)
		image_data = self.get_image_stats(winner_competitor, initial_index=winner_image_index)
		data[f"competitor-{winner_position}"]["competitor"] = winner_competitor
		data[f"competitor-{winner_position}"]["rating"] = self.get_rating_stat(winner_competitor)
		data[f"competitor-{winner_position}"]["images"] = image_data["images"]
		data[f"competitor-{winner_position}"]["initial_index"] = winner_image_index
		data[f"competitor-{winner_position}"]["forloop_index"] = winner_image_index+1
		
		for i in range(1, competitors_number+1):
			if i != int(winner_position):
				competitor_number = i
				competitor_number_key = f"competitor-{competitor_number}"
				competitor = self.competitor_service.get_competitor(enemy_id)
				data[competitor_number_key]["competitor"] = competitor
				competitors.append(competitor)
				image_data = self.get_image_stats(competitor)
				data[competitor_number_key]["rating"] = self.get_rating_stat(competitor)
				data[competitor_number_key]["images"] = image_data["images"]
				data[competitor_number_key]["initial_index"] = 0
				data[competitor_number_key]["forloop_index"] = 1
		data = dict(sorted(data.items()))
		return data