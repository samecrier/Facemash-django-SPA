class EloRatingSystem():
	@staticmethod
	def get_cost(winner_rating, loser_rating, K=32) -> int:
		winner_expected_result = 1/(1+10**((loser_rating-winner_rating)/400))
		rating_cost = K * (1-winner_expected_result)
		return rating_cost