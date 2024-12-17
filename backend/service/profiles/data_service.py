from service.competitors.service import LocalCompetitorService
from service.matchups.service import LocalMatchupService
from service.ratings.service import LocalRatingService
from collections import defaultdict

class ProfileGetData():
	
	def __init__(
			self,
			competitor_service=LocalCompetitorService(),
		):
		self.competitor_service = competitor_service

	def get_n_profile_matchups(self, profile_id, number=None):
		"""
		Получает number количество матчапов для профиля

		:param profile_id: Profile
		:param number: int - количество матчапов
		return dict
		"""
		matchups = LocalMatchupService.get_profile_matchups(profile_id).order_by('-created_at')
		if number:
			matchups = matchups[:number]
	
		competitor_ids = self.competitor_service.get_competitors_from_matchups(matchups)
		ratings = LocalRatingService.get_rating_profiles(profile_id, competitor_ids)
		
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
