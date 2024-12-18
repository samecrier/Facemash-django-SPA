from django.db import models

# Create your models here.
class TournamentSystem(models.model):
	system_name = models.CharField(max_length=255)
	created_at = models.DateTimeField(auto_now_add=True)
	
	def __str__(self):
		return f'{self.name}'


class TournamentRatingSystem(models.Model):
	rating_system_name = models.CharField(max_length=255)
	created_at = models.DateTimeField(auto_now_add=True)
	
	def __str__(self):
		return f'{self.name}'


class TemplateTournament(models.Model):
	STATUS_CHOICES = [
		('available', 'available'),    # Завершён
		('archieved', 'archieved'),      # Отменён
	]

	template_name = models.CharField(max_length=255)
	competitors_number = models.PositiveIntegerField()
	rounds_number = models.PositiveIntegerField()
	creator_id = models.ForeignKey(
		'profiles.User',
		on_delete=models.SET_NULL,
		null=True,
		related_name='template_tournaments',
		db_column='creator_id'
	)
	status = models.CharField(
		max_length=255,
		choices=STATUS_CHOICES, 
		default='available')
	created_at = models.DateTimeField(auto_now_add=True)


class TemplateRound(models.Model):
	template_tournament_id = models.ForeignKey(
		'tournaments.TemplateTournament',
		on_delete=models.CASCADE,
		related_name='template_rounds',
		db_column='template_tournament_id'
	)
	tournament_rating_system_id = models.ForeignKey(
		'tournaments.TournamentRatingSystem',
		on_delete=models.PROTECT,
		related_name='template_rounds',
		db_column='tournament_rating_system_id'
	)
	round_number = models.PositiveIntegerField()
	competitors_in_matchup = models.PositiveIntegerField()
	created_at = models.DateTimeField(auto_now_add=True)


class TournamentBase(models.Model):
	STATUS_CHOICES = [
		('not started', 'not started'),
		('in progress', 'in progress'),
		('completed', 'completed')
	]
	profile_id = models.ForeignKey(
		'profiles.User',
		on_delete=models.CASCADE,
		related_name='tournaments',
		db_column='profile_id'
	)
	template_tournament_id = models.ForeignKey(
		'tournaments.TemplateTournament',
		on_delete=models.PROTECT,
		related_name='template_rounds',
		db_column='template_tournament_id'
	)
	competitors_number = models.PositiveIntegerField()
	rounds_number = models.PositiveIntegerField()
	status = models.CharField(
		max_length=255,
		choices=STATUS_CHOICES, 
		default='not started')
	winner_id = models.ForeignKey(
		'competitors.Competitor',
		on_delete=models.SET_NULL,
		null=True, blank=True,
		related_name='tournaments_win',
		db_column='winner_id'
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)


class TournamentCompetitor(models.Model):
	STATUS_CHOICES = [
		('active', 'active'),
		('eliminated', 'eliminated')
	]
	competitor_id = models.ForeignKey(
		'competitors.Competitor',
		on_delete=models.CASCADE,
		related_name='tournament_participation',
		db_column='competitor_id'
	)
	tournament_base_id = models.ForeignKey(
		'tournaments.TournamentBase',
		on_delete=models.CASCADE,
		related_name='tournament_competitors',
		db_column='tournament_base_id'
	)
	status = models.CharField(
		max_length=255,
		choices=STATUS_CHOICES
		)
	final_position = models.PositiveIntegerField(null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)


class TournamentRound(models.Model):
	STATUS_CHOICES = [
		('not started', 'not started'),
		('in progress', 'in progress'),
		('completed', 'completed')
	]

	tournament_base_id = models.ForeignKey(
		'tournaments.TournamentBase',
		on_delete=models.CASCADE,
		related_name='tournament_rounds',
		db_column='tournament_base_id'
	)
	round_number = models.PositiveIntegerField()
	competitors_in_matchup = models.PositiveIntegerField()
	status = models.CharField(
		max_length=255,
		choices=STATUS_CHOICES, 
		default='not started')
	winners = models.ManyToManyField(
		'competitors.TournamentCompetitor',
		related_name='tournament_round_winners'
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)


class RoundCompetitor(models.Model):
	STATUS_CHOICES = [
		('qualified', 'qualified'),
		('eliminated', 'eliminated'),
		('not played', 'not played')
	]
	RESULT_CHOICES = [
		(0, 'Lose'),        # Проиграл
		(1, 'Win'),         # Выиграл
	]
	
	tournament_competitor_id = models.ForeignKey(
		'tournaments.TournamentCompetitor',
		on_delete=models.CASCADE,
		related_name='tournament_competitor_rounds',
		db_column='tournament_competitor_id'
	)
	tournament_round_id = models.ForeignKey(
		'tournaments.TournamentRound',
		on_delete=models.CASCADE,
		related_name='round_competitors',
		db_column='tournament_round_id'
	)
	status = models.CharField(
		max_length=255,
		choices=STATUS_CHOICES,
		default='not played'
		)
	result = models.IntegerField(choices=RESULT_CHOICES, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)


class TournamentMatchup:

	tournament_round_id = models.ForeignKey(
		'tournaments.TournamentRound',
		on_delete=models.CASCADE,
		related_name='round_matchups',
		db_column='tournament_round_id'
	)
	competitors_in_matchup = models.ManyToManyField(
		'tournaments.RoundCompetitor',
		related_name='matchups'
	)
	winner_id = models.ForeignKey(
		'tournaments.RoundCompetitor',
		on_delete=models.CASCADE,
		related_name='matchups_winners',
		db_column='winner_id'
	)
	losers = models.ManyToManyField(
		'tournaments .RoundCompetitor',
		related_name='matchups_losers'
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
