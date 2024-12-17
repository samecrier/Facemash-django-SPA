from abc import ABC, abstractmethod

class EloRatingSystem(ABC):
	
	@abstractmethod
	def delta(winner_rating, loser_rating) -> int:
		pass

class EloRatingSystem32(EloRatingSystem):
	
	K_RATIO = 32
	
	def delta(self, winner_rating, loser_rating) -> int:
		winner_expected_result = 1/(1+10**((loser_rating-winner_rating)/400))
		delta = self.K_RATIO * (1-winner_expected_result)
		return delta
	
	def __str__(self):
		return f"elo_{self.K_RATIO}"

class EloRatingSystem64(EloRatingSystem):
	
	K_RATIO = 64
	
	def delta(self, winner_rating, loser_rating) -> int:
		winner_expected_result = 1/(1+10**((loser_rating-winner_rating)/400))
		delta = self.K_RATIO * (1-winner_expected_result)
		return delta
	
	def __str__(self):
		return f"elo_{self.K_RATIO}"