from django.db import models
from django.contrib.contenttypes.models import ContentType

# Create your models here.
class Rating(models.Model):
	competitor_id = models.OneToOneField(
		'competitors.Competitor',
		on_delete=models.CASCADE,
		related_name='rating',
		db_column='competitor_id')
	rating = models.PositiveIntegerField(default=1200)
	wins = models.IntegerField(default=0)
	losses = models.IntegerField(default=0)
	matchups = models.IntegerField(default=0)
	tournaments = models.IntegerField(default=0)
	updated_at = models.DateTimeField(auto_now=True)

class RatingProfile(models.Model):
	profile_id = models.ForeignKey(
		'profiles.User', 
		on_delete=models.CASCADE, 
		related_name='ratings',
		db_column='profile_id'
	)
	competitor_id = models.ForeignKey(
		'competitors.Competitor', 
		on_delete=models.CASCADE,
		related_name='profiles_ratings',
		db_column='competitor_id'
	)
	rating = models.PositiveIntegerField(default=1200)
	wins = models.IntegerField(default=0)
	losses = models.IntegerField(default=0)
	matchups = models.IntegerField(default=0)
	tournaments = models.IntegerField(default=0)
	updated_at = models.DateTimeField(auto_now=True)