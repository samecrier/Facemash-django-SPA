from services.competitors_service import LocalCompetitorService
from services.ratings_service import LocalRatingService
from services.profiles_service import LocalProfileService
from services.matchups_service import LocalMatchupService
from django.utils.safestring import mark_safe
import json
from collections import defaultdict

class GetData():
	competitor_service = LocalCompetitorService()
	rating_service = LocalRatingService()
	profile_service = LocalProfileService()
	matchup_service = LocalMatchupService()

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
						data[competitor_number_key]["competitor"]["name"] = competitor.name
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
		data["id"] = competitor_obj.id
		data["age"] = competitor_obj.age
		data["city"] = competitor_obj.city.city_eng
		image_data = self.get_image_stats(competitor_obj)
		data["rating"] = self.rating_service.get_rating(competitor_obj)
		data["images"] = image_data["images"]
		data["bio"] = self.competitor_service.get_competitor_bio(competitor_obj)
		if not data["bio"]:
			data["bio"] = '-'
		return data

	def get_specific_matchup_guest(self, winner_id, winner_position, winner_image_index, 
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
	
	def get_saved_data(self, competitor_1, competitor_2, competitor_1_index=0, competitor_2_index=0):
		data = defaultdict(dict)
		competitor_1_index = int(competitor_1_index)
		image_data = self.get_image_stats(competitor_1, initial_index=competitor_1_index)
		data["competitor-1"]["competitor"] = competitor_1
		data["competitor-1"]["rating"] = self.get_rating_stat(competitor_1)
		data["competitor-1"]["images"] = image_data["images"]
		data["competitor-1"]["initial_index"] = competitor_1_index
		data["competitor-1"]["forloop_index"] = competitor_1_index+1
		
		data["competitor-2"]["competitor"] = competitor_2
		image_data = self.get_image_stats(competitor_2, initial_index=competitor_2_index)
		data["competitor-2"]["rating"] = self.get_rating_stat(competitor_2)
		data["competitor-2"]["images"] = image_data["images"]
		data["competitor-2"]["initial_index"] = competitor_2_index
		data["competitor-2"]["forloop_index"] = competitor_2_index+1
		data = dict(sorted(data.items()))
		return data
	
	def get_specific_matchup(self, competitor_1, competitor_2, competitor_1_position=1, competitor_1_index=0, competitors_number=2):
		data = defaultdict(dict)
		competitor_1_index = int(competitor_1_index)
		competitors = []
		competitor_1 = self.competitor_service.get_competitor(competitor_1)
		competitors.append(competitor_1)
		image_data = self.get_image_stats(competitor_1, initial_index=competitor_1_index)
		data[f"competitor-{competitor_1_position}"]["competitor"] = competitor_1
		data[f"competitor-{competitor_1_position}"]["rating"] = self.get_rating_stat(competitor_1)
		data[f"competitor-{competitor_1_position}"]["images"] = image_data["images"]
		data[f"competitor-{competitor_1_position}"]["initial_index"] = competitor_1_index
		data[f"competitor-{competitor_1_position}"]["forloop_index"] = competitor_1_index+1
		
		for i in range(1, competitors_number+1):
			if i != int(competitor_1_position):
				competitor_number = i
				competitor_number_key = f"competitor-{competitor_number}"
				competitor = self.competitor_service.get_competitor(competitor_2)
				data[competitor_number_key]["competitor"] = competitor
				competitors.append(competitor)
				image_data = self.get_image_stats(competitor)
				data[competitor_number_key]["rating"] = self.get_rating_stat(competitor)
				data[competitor_number_key]["images"] = image_data["images"]
				data[competitor_number_key]["initial_index"] = 0
				data[competitor_number_key]["forloop_index"] = 1
		data = dict(sorted(data.items()))
		return data
	
	def get_saved_matchup(self, request):
		if request.user.is_authenticated:
			try:
				saved_matchup = request.user.saved_matchup
				return saved_matchup
			except:
				competitor_1 = self.competitor_service.get_random_competitor()
				while True:
					competitor_2 = self.competitor_service.get_random_competitor()
					if competitor_2 != competitor_1:
						saved_matchup = self.matchup_service.create_saved_matchup(
							request.user, competitor_1, competitor_2)
						return saved_matchup
				
		else:
			return False

	def update_saved_matchup(self, profile_id, winner_id, winner_position,
		winner_image_index, enemy_id):
		winner_id = self.competitor_service.get_competitor(winner_id)
		enemy_id = self.competitor_service.get_competitor(enemy_id)
		if winner_position == '1':
			updated_matchup = self.matchup_service.update_saved_matchup(
				profile_id=profile_id, 
				competitor_1=winner_id,
				competitor_2=enemy_id,
				competitor_1_ii=winner_image_index,
				competitor_2_ii=0
			)
		else:
			updated_matchup = self.matchup_service.update_saved_matchup(
				profile_id=profile_id, 
				competitor_1=enemy_id,
				competitor_2=winner_id,
				competitor_1_ii=0,
				competitor_2_ii=winner_image_index
			)
		return updated_matchup
	
	def get_two_competitors(self):
		competitor_1 = self.competitor_service.get_random_competitor()
		while True:
			competitor_2 = self.competitor_service.get_random_competitor()
			if competitor_2 != competitor_1:
				break
		return (competitor_1, competitor_2)
	

	def get_profile_matchups(self, profile_id, number=None):
		matchups = self.matchup_service.get_profile_matchups(profile_id).order_by('-created_at')
		if number:
			matchups = matchups[:number]
	
		competitor_ids = self.competitor_service.get_competitors_from_matchups(matchups)
		ratings = self.rating_service.get_rating_profiles(profile_id, competitor_ids)
		
		data = defaultdict(dict)
		for i, matchup in enumerate(matchups):
			i = i+1
			data[i]["winner"] = matchup.winner_id
			data[i]["loser"] = matchup.loser_id
			data[i]["winner_rating"] = ratings[matchup.winner_id]
			data[i]["loser_rating"] = ratings[matchup.loser_id]
			data[i]["delta_winner"] = matchup.delta_winner_profile
			data[i]["delta_loser"] = matchup.delta_loser_profile
			ratings[matchup.winner_id] -= matchup.delta_winner_profile
			ratings[matchup.loser_id] += matchup.delta_loser_profile
		data = dict(data)
		return data
	
	def paginate_dict(data, page=1, per_page=10):
		"""
		Пагинация словаря с числовыми ключами.
		
		:param data: dict - исходный словарь
		:param page: int - текущая страница (по умолчанию 1)
		:param per_page: int - количество элементов на странице (по умолчанию 10)
		:return: dict - часть словаря, соответствующая странице
		"""
		if not isinstance(data, dict):
			raise ValueError("Data must be a dictionary")

		# Сортируем словарь по ключам
		sorted_keys = sorted(data.keys())
		
		# Определяем границы текущей страницы
		start = (page - 1) * per_page
		end = start + per_page

		# Извлекаем нужные элементы
		paginated_keys = sorted_keys[start:end]
		paginated_dict = {key: data[key] for key in paginated_keys}

		return paginated_dict
