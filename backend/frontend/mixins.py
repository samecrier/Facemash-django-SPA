from django.http import HttpResponseForbidden
from django.http import Http404
from django.shortcuts import redirect
from services.tournaments.service import LocalTournamentService
from services.competitors.data_service import CompetitorGetData
from services.tournaments.helper import TournamentHelper

class BasePermissionMixin:
	tournament_lookup_field = "tournament_id"
	tournament_service = LocalTournamentService()
	
	def get_tournament_obj(self, tournament_id, request):
		"""Получение объекта турнира и проверка прав доступа."""
		tournament_obj = self.tournament_service.base.get_tournament_obj(tournament_id)
		if not tournament_obj:
			raise Http404("Такого турнира не существует")
		if tournament_obj.profile_id != request.user:
			raise HttpResponseForbidden("У вас нет доступа к этому турниру.")
		return tournament_obj

	def get_round_obj(self, tournament_obj, round_number):
		"""Получение объекта раунда и проверка актуальности."""
		round_obj = self.tournament_service.round.get_round_obj_by_tournament(tournament_obj, round_number)
		if not round_obj:
			raise Http404("Такого раунда не существует")
		
		if not self.helper_service.check_actuality_round_obj(tournament_obj, round_obj):
			raise Http404("Этот раунд еще не инициализирован")
		return round_obj


class TournamentPermissionMixin(BasePermissionMixin):
	tournament_lookup_field = "tournament_id"
	
	def dispatch(self, request, *args, **kwargs):
		tournament_id = kwargs.get(self.tournament_lookup_field)
		tournament_obj = self.get_tournament_obj(tournament_id, request)
		self.tournament_obj = tournament_obj
		return super().dispatch(request, *args, **kwargs)
	
class RoundPermissionMixin(BasePermissionMixin):
	round_lookup_field = "round_number"
	
	def dispatch(self, request, *args, **kwargs):
		tournament_id = kwargs.get(self.tournament_lookup_field)
		round_number = kwargs.get(self.round_lookup_field)
		
		tournament_obj = self.get_tournament_obj(tournament_id, request)
		round_obj = self.get_round_obj(tournament_obj, round_number)
		
		self.tournament_obj = tournament_obj
		self.round_obj = round_obj
		return super().dispatch(request, *args, **kwargs)
	

class MatchupPermissionMixin(BasePermissionMixin):
	round_lookup_field = "round_number"
	matchup_number_lookup_field = "matchup_number"
	helper_service = TournamentHelper()
	
	def dispatch(self, request, *args, **kwargs):
		tournament_id = kwargs.get(self.tournament_lookup_field)
		round_number = kwargs.get(self.round_lookup_field)
		matchup_number = kwargs.get(self.matchup_number_lookup_field)
		
		tournament_obj = self.get_tournament_obj(tournament_id, request)
		round_obj = self.get_round_obj(tournament_obj, round_number)
		

		competitors_in_matchup, matchup_obj = self.helper_service.get_actual_matchup(round_obj, matchup_number)
		if not matchup_obj:
			if matchup_number:
				raise Http404("Такого матчапа не существует")
			else:
				next_round_number = self.helper_service.turn_next_round(tournament_obj, round_number)
				if not next_round_number:
					return redirect('tournament-winner', tournament_id)
				return redirect('tournament-stage', tournament_id, next_round_number)

		
		self.tournament_obj = tournament_obj
		self.round_obj = round_obj
		self.competitors_in_matchup = competitors_in_matchup
		self.matchup_obj = matchup_obj
		return super().dispatch(request, *args, **kwargs)
	
class WinnerPermissionMixin(BasePermissionMixin):
	helper_service = TournamentHelper()
	data_service = CompetitorGetData()

	def dispatch(self, request, *args, **kwargs):
		tournament_id = kwargs.get(self.tournament_lookup_field)
		
		tournament_obj = self.get_tournament_obj(tournament_id, request)
		competitor_obj = self.helper_service.get_winner_competitor_obj(tournament_obj)
		if not competitor_obj:
			raise Http404("У этого турнира еще нет победителя")
		
		self.tournament_obj = tournament_obj
		self.competitor_obj = competitor_obj
		return super().dispatch(request, *args, **kwargs)