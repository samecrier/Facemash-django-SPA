from django.db import models
from services.competitors.service import LocalCompetitorService

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
	delta_winner_profile = models.IntegerField(null=True)
	delta_loser_profile = models.IntegerField(null=True)
	profile_id = models.ForeignKey(
		'profiles.User',
		on_delete=models.SET_NULL,
		null=True,
		related_name='matchups',
		db_column='profile_id'
	)
	tournament_matchup_id = models.ForeignKey(
		'tournaments.TournamentMatchup',
		on_delete=models.SET_NULL,
		null=True, blank=True,
		related_name='matchups',
		db_column='tournament_matchup_id'
	)
	created_at = models.DateTimeField(auto_now_add=True)

	competitor_service = None
	def __init__(self, *args, competitor_service=None, **kwargs):
		super().__init__(*args, **kwargs)
		if not competitor_service:
			self.competitor_service = LocalCompetitorService()
		else:
			self.competitor_service = competitor_service

	def get_winner(self):
		return(self.competitor_service.get_competitor_object(self.winner_id))
	
	def get_loser(self):
		return(self.competitor_service.get_competitor_object(self.loser))
	
	def __str__(self):
		return f"{self.winner_id} vs {self.loser_id}"

class SavedMatchup(models.Model):
	profile_id = models.OneToOneField(
		'profiles.User',
		on_delete=models.CASCADE,
		related_name='saved_matchup',
		db_column='profile_id'
	)
	competitor_1 = models.ForeignKey(
		'competitors.Competitor',
		on_delete=models.CASCADE,
		related_name='saved_first_competitor'
	)
	competitor_2 = models.ForeignKey(
		'competitors.Competitor',
		on_delete=models.CASCADE,
		related_name='saved_second_competitor'
	)
	competitor_1_ii = models.PositiveIntegerField(default=0)
	competitor_2_ii = models.PositiveIntegerField(default=0)
	updated_at = models.DateTimeField(auto_now=True)
	