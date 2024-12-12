from django.db import models
from services.competitors_service import LocalCompetitorService

# Create your models here.
class Matchup(models.Model):
	winner_id = models.ForeignKey(
		'competitors.Competitor',
		on_delete=models.SET_NULL,
		null=True,
		related_name='wins',
		db_column='winner_id'
	)
	loser_id = models.ForeignKey(
		'competitors.Competitor',
		on_delete=models.SET_NULL,
		null=True,
		related_name='losses',
		db_column='loser_id'
	)
	rating_system = models.CharField(max_length=255)
	delta_winner = models.IntegerField()
	delta_loser = models.IntegerField()
	created_at = models.DateTimeField(auto_now_add=True)

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