from services.competitors_service import LocalCompetitorService
from django.utils.safestring import mark_safe
import json
from collections import defaultdict

class GetData():
	competitor_service = LocalCompetitorService()
	
	def get_image_stats(self, competitor, initial_index=0) -> list:
		images = [image.get_path() for image in competitor.images.all()]
		images.sort()
		initial_index = int(initial_index)
		initial_image = images[initial_index]
		image_count = len(images)
		other_images = mark_safe(json.dumps(images))
		images = mark_safe(json.dumps(images))
		print(f"first{initial_image}, {images}")
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
			image_data = self.get_image_stats(competitor)
			data[competitor_number_key]["images"] = image_data["images"]
			data[competitor_number_key]["initial_index"] = 0
			data[competitor_number_key]["forloop_index"] = 1
		data = dict(data)
		return data
	
	def get_enemy(self, competitors_number, winner_id, winner_position, current_image_index) -> dict:
		data = defaultdict(dict)
		current_image_index = int(current_image_index)
		competitors = []
		winner_competitor = self.competitor_service.get_competitor(winner_id)
		competitors.append(winner_competitor)
		image_data = self.get_image_stats(winner_competitor, initial_index=current_image_index)
		data[f"competitor-{winner_position}"]["competitor"] = winner_competitor
		data[f"competitor-{winner_position}"]["images"] = image_data["images"]
		data[f"competitor-{winner_position}"]["initial_index"] = current_image_index
		data[f"competitor-{winner_position}"]["forloop_index"] = current_image_index+1
		
		for i in range(1, competitors_number+1):
			if i != int(winner_position):
				competitor_number = i
				competitor_number_key = f"competitor-{competitor_number}"
				competitor = self.competitor_service.get_random_competitor()
				while True:
					competitor = self.competitor_service.get_random_competitor()
					if competitor not in competitors:
						data[competitor_number_key]["competitor"] = competitor
						competitors.append(competitor)
						break
				image_data = self.get_image_stats(competitor)
				data[competitor_number_key]["images"] = image_data["images"]
				data[competitor_number_key]["initial_index"] = 0
				data[competitor_number_key]["forloop_index"] = 1
		data = dict(sorted(data.items()))
		return data
