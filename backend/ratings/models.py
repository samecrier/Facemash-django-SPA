from django.db import models
from django.contrib.contenttypes.models import ContentType

# Create your models here.
class Rating(models.Model):
	competitor_id = True
	rating = True
	wins = True
	loses = True
	matchups = True
	updated_at = True