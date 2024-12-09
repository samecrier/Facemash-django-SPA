from django.db import models
from services.competitors_service import LocalCompetitorService

# Create your models here.
class Matchup(models.Model):
	winner_id = models.IntegerField()
	loser_id = models.IntegerField()
	rating_system = models.CharField(max_length=255)
	winner_rating_change = True
	loser_rating_change = True
	created_at = True

	competitor_service = None
	def __init__(self, *args, competitor_service=None, **kwargs):
		super().__init__(*args, **kwargs)
		if not competitor_service:
			self.competitor_service = LocalCompetitorService()
		else:
			self.competitor_service = competitor_service

	def get_winner(self):
		return(self.competitor_service.get_competitor(self.winner_id))
	
	def get_loser(self):
		return(self.competitor_service.get_competitor(self.loser))