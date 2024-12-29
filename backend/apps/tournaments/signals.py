from django.db.models.signals import pre_delete
from django.dispatch import receiver
from apps.tournaments.models import TournamentBase, TournamentRound, TournamentMatchup


@receiver(pre_delete, sender=TournamentBase)
def delete_pending_matchups(sender, instance, **kwargs):
	instance.competitors.filter(status='not started').delete()

@receiver(pre_delete, sender=TournamentRound)
def delete_pending_matchups(sender, instance, **kwargs):
	instance.round_competitors.filter(status='in schedule').delete()
	instance.round_matchups.filter(winner_id__isnull=True).delete()