from services.competitors.service import LocalCompetitorService
from services.matchups.service import LocalMatchupService
from services.ratings.service import LocalRatingService
from typing import TYPE_CHECKING, Tuple
if TYPE_CHECKING:
	from apps.competitors.models import Competitor
	from apps.matchups.models import SavedMatchup

class MatchupHelper():
	
	def __init__(
			self,
			competitor_service=LocalCompetitorService(),
			rating_service=LocalRatingService()
		):
		self.competitor_service = competitor_service
		self.rating_service = rating_service
	
	def get_two_competitors(self) -> Tuple['Competitor', 'Competitor']:
		"""
		Возвращает два рандомных компетитора
		return (Competitor, Competitor)
		"""
		competitor_1 = self.competitor_service.get_random_competitor()
		while True:
			competitor_2 = self.competitor_service.get_random_competitor()
			if competitor_2 != competitor_1:
				break
		return (competitor_1, competitor_2)
	
	def get_winner_rating(self, winner_id) -> int:
		"""
		По строке с айди возвращает рейтинг компетитора

		:param winner_id:Competitor|str(competitor.id)
		return Rating.rating
		"""
		return self.rating_service.get_rating(winner_id)
	
	def get_rating_stat(self, competitor) -> int :
		"""
		Возвращает рейтинг объекта Competitor

		:param competitor: Competitor 
		return Rating.rating
		"""

		return self.rating_service.get_rating(competitor)


class SavedMatchupHelper():

	def __init__(
			self,
			competitor_service=LocalCompetitorService(),
			matchup_service=LocalMatchupService()
		):
		self.competitor_service = competitor_service
		self.matchup_service = matchup_service

	def update_saved_matchup(self, profile_id, winner_id, winner_position,
		winner_image_index, enemy_id) -> 'SavedMatchup':
		"""
		Обновляет последний сохраненный матчап и получает этот объект

		:param profile_id: Profile, 
		:param winner_id/enemy_id: str(Competitor.id)
		:param winner_position: int - позиция на странице
		:param winner_image_index: int -индекс фотографии
		return SavedMatchup
		"""
		winner_id = self.competitor_service.get_competitor_object(winner_id)
		enemy_id = self.competitor_service.get_competitor_object(enemy_id)
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
	
	def get_saved_matchup(self, request) -> 'SavedMatchup':
		"""
		Получает или создает сохраненный матчап

		:param request: request
		return SavedMatchup|False
		"""
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