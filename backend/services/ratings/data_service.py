from services.ratings.service import LocalRatingService

class RatingData:

	service = LocalRatingService()
	
	def get_competitor_data(self, competitor_obj, rating):
		competitor_data = {
				'id': competitor_obj.id,
				'name': competitor_obj.name,
				'name_id': competitor_obj.name_id,
				'age': competitor_obj.age,
				'city': competitor_obj.city.city_eng,
				'rating': rating
			}
		return competitor_data

	def get_data_top_rating(self, number):
		data = {}
		top_rating = self.service.get_top_rating(number)
		for competitor_obj, rating in top_rating:
			data[competitor_obj.id] = self.get_competitor_data(competitor_obj, rating)
		return data

	def get_data_top_ratingprofile(self, user, number):
		data = {}
		top_rating = self.service.get_top_ratingprofile(user, number)
		for competitor_obj, rating in top_rating:
			data[competitor_obj.id] = self.get_competitor_data(competitor_obj, rating)
		return data