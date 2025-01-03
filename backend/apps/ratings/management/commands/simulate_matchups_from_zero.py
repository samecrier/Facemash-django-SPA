from django.core.management.base import BaseCommand
from apps.matchups.models import Matchup
from apps.competitors.models import Competitor
from apps.profiles.models import User
from apps.ratings.models import RatingProfile


class Command(BaseCommand):
	help = "Использовать только в пустой базе"

	def handle(self, *args, **kwargs):
		
		matchups = Matchup.objects.all()

		for matchup in matchups:
			profile = matchup.profile_id
			winner = matchup.winner_id
			loser = matchup.loser_id
	
			winner_rp, winner_created = RatingProfile.objects.get_or_create(
				profile_id=profile,
				competitor_id = winner
			)

			loser_rp, loser_created = RatingProfile.objects.get_or_create(
				profile_id=profile,
				competitor_id = loser
			)
		
		
			winner_rp.rating += matchup.delta_winner_profile
			winner_rp.wins += 1
			winner_rp.matchups += 1
			winner_rp.save()
	
			loser_rp.rating += matchup.delta_loser_profile
			loser_rp.losses += 1
			loser_rp.matchups += 1
			loser_rp.save()