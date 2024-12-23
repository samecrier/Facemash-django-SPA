from django.db import models

# Create your models here.
class TournamentSystem(models.Model):
	system_name = models.CharField(max_length=255)
	created_at = models.DateTimeField(auto_now_add=True)
	
	def __str__(self):
		return f'{self.system_name}'


class TournamentRatingSystem(models.Model):
	rating_system_name = models.CharField(max_length=255)
	created_at = models.DateTimeField(auto_now_add=True)
	
	def __str__(self):
		return f'{self.rating_system_name}'


class TemplateTournament(models.Model):
	STATUS_CHOICES = [
		('available', 'available'),
		('archived', 'archived'),
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
		db_column='template_round'
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
		('completed', 'completed'),
		('archived', 'archived')
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
		related_name='tournaments',
		db_column='template_tournament_id',
		null=True, blank=True
	)
	competitors_number = models.PositiveIntegerField()
	competitors_remaining = models.PositiveIntegerField()
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
		('not started', 'not started'),
		('active', 'active'),
		('eliminated', 'eliminated'),
		('winner', 'winner')
	]
	tournament_base_id = models.ForeignKey(
		'tournaments.TournamentBase',
		on_delete=models.SET_NULL,
		related_name='competitors',
		db_column='tournament_base_id',
		null=True
	)
	competitor_id = models.ForeignKey(
		'competitors.Competitor',
		on_delete=models.CASCADE,
		related_name='tournaments_participation',
		db_column='competitor_id'
	)
	status = models.CharField(
		max_length=255,
		choices=STATUS_CHOICES,
		default='not started'
		)
	final_position = models.PositiveIntegerField(null=True, blank=True)
	delta_tournament = models.IntegerField(default=0)
	delta_tournament_profile = models.IntegerField(default=0)
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
		related_name='rounds',
		db_column='tournament_base_id'
	)
	rating_system = models.CharField(max_length=255, default='elo_64')
	round_number = models.PositiveIntegerField(default=1)
	competitors_in_matchup = models.PositiveIntegerField()
	status = models.CharField(
		max_length=255,
		choices=STATUS_CHOICES, 
		default='not started')
	winners = models.ManyToManyField(
		'tournaments.TournamentCompetitor',
		related_name='round_winners'
	)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)


class RoundCompetitor(models.Model):
	STATUS_CHOICES = [
		('qualified', 'qualified'),
		('eliminated', 'eliminated'),
		('in schedule', 'in schedule'),
		('not played', 'not played')
	]
	RESULT_CHOICES = [
		(0, 'Lose'),
		(1, 'Win')
	]
	
	tournament_competitor_id = models.ForeignKey(
		'tournaments.TournamentCompetitor',
		on_delete=models.CASCADE,
		related_name='round_status',
		db_column='tournament_competitor_id'
	)
	tournament_round_id = models.ForeignKey(
		'tournaments.TournamentRound',
		on_delete=models.SET_NULL,
		related_name='round_competitors',
		db_column='tournament_round_id',
		null=True
	)
	delta_round = models.IntegerField(default=0)
	delta_round_profile = models.IntegerField(default=0)
	status = models.CharField(
		max_length=255,
		choices=STATUS_CHOICES,
		default='not played'
		)
	result = models.IntegerField(choices=RESULT_CHOICES, null=True, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)


class TournamentMatchup(models.Model):
	
	tournament_round_id = models.ForeignKey(
		'tournaments.TournamentRound',
		on_delete=models.SET_NULL,
		related_name='round_matchups',
		db_column='tournament_round_id',
		null=True
	)
	competitors_in_matchup = models.ManyToManyField(
		'tournaments.RoundCompetitor',
		related_name='matchups'
	)
	winner_id = models.ForeignKey(
		'tournaments.RoundCompetitor',
		on_delete=models.CASCADE,
		related_name='matchup_winner',
		db_column='winner_id',
		null=True, blank=True
	)
	losers = models.ManyToManyField(
		'tournaments.RoundCompetitor',
		related_name='matchup_losers'
	)
	matchup_number = models.PositiveIntegerField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
