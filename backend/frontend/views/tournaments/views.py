from django.http import HttpResponse, Http404, HttpResponseForbidden
from django.db import transaction
from django.urls import reverse
from django.views import View
from django.shortcuts import render, redirect
from apps.tournaments.forms import TournamentSelectionForm
from frontend.mixins import TournamentPermissionMixin, RoundPermissionMixin, MatchupPermissionMixin, WinnerPermissionMixin
from services.competitors.service import LocalCompetitorService
from services.competitors.data_service import CompetitorGetData
from services.tournaments.service import LocalTournamentService
from services.matchups.data_service import MatchupGetData
from services.tournaments.data_service import TournamentGetData
from services.tournaments.helper import TournamentHelper
from services.tournaments.handler import TournamentHandler
from apps.tournaments.models import TournamentBase
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin


class HomeTournamentView(LoginRequiredMixin, View):
	
	helper_service = TournamentHelper()
	
	def get(self, request):
		
		profile_obj = request.user
		
		data = self.helper_service.get_tournaments_base(profile_obj)
		return render(request, 'frontend/tournaments/main.html',
			{'data': data}
		)


class CreateTournamentView(LoginRequiredMixin, View):
	helper_service = TournamentHelper()
	competitor_service = LocalCompetitorService()
	handler_service = TournamentHandler()
	data_service = TournamentGetData()
	
	def get(self, request):
		tournament_form = TournamentSelectionForm()
		return render(request, 'frontend/tournaments/create.html', {'tournament_form': tournament_form})
	
	def post(self, request):
		tournament_form = TournamentSelectionForm(request.POST)  # Заполняем форму данными POST
		if tournament_form.is_valid():  # Проверяем валидацию
			# Получаем выбранные города
			cities = tournament_form.cleaned_data['cities']
			participants = tournament_form.cleaned_data['num_participants']
			rounds = tournament_form.cleaned_data['num_rounds']
			in_matchup = tournament_form.cleaned_data['num_per_matchup']
			result = self.helper_service.check_correct_tournament_information(participants, rounds, in_matchup)
			if not result:
				raise Http404('Неправильные данные для турнира')
			tournament_id, round_number = self.handler_service.process_tournament(request, cities, participants, rounds, in_matchup)
			return redirect('tournament-stage', tournament_id, round_number) # Редирект при успешной обработке
		else:
			# Возвращаем форму с ошибками
			return render(request, 'frontend/tournaments/create.html', {'tournament_form': tournament_form})


class TournamentView(LoginRequiredMixin, TournamentPermissionMixin, View):
	helper_service = TournamentHelper()
	
	def get(self, request, tournament_id):
		competitors = self.helper_service.get_competitors_info(tournament_id)
		actual_rounds_status = self.helper_service.actual_rounds_status(tournament_id)
		actual_round = self.helper_service.get_actual_round_obj_by_tournament(tournament_id)
		paginator = Paginator(competitors, 20)
		page_number = request.GET.get('page', 1)
		page_obj = paginator.get_page(page_number)
		start_position = (page_obj.number - 1) * paginator.per_page
		return render(request, 'frontend/tournaments/info.html', {
			'page_obj': page_obj,
			'paginator': paginator,
			'start_position': start_position,
			'tournament_obj': self.tournament_obj,
			'actual_round': actual_round,
			'actual_rounds_status': actual_rounds_status
		})

class StageTournamentView(LoginRequiredMixin, RoundPermissionMixin, View):
	helper_service = TournamentHelper()
	data_service = TournamentGetData()
	
	def get(self, request, tournament_id, round_number):
		
		matchups = self.helper_service.get_stage_matchups(self.round_obj)
		data = self.data_service.get_data_stage(request, matchups)
		return render(request, 'frontend/tournaments/stage.html',
			{
				'data': data
			})


class MatchupTournamentView(LoginRequiredMixin, MatchupPermissionMixin, View):
	helper_service = TournamentHelper()
	data_service = MatchupGetData()
	handler=TournamentHandler()

	def get(self, request, tournament_id, round_number, matchup_number=None):
		tournament = {
			'id': self.tournament_obj.id,
			'winner_id': self.tournament_obj.winner_id,
		}

		competitors_number = len(self.competitors_in_matchup)
		matchups_count = self.helper_service.get_count_matchup_in_round(tournament_id, round_number)
		data = self.data_service.data_matchup(**self.competitors_in_matchup)
		return render(request, 'frontend/tournaments/tournament_matchup.html',
			{	
				'matchups_count': matchups_count,
				'competitors_number': competitors_number,
				'data': data,
				'matchup': self.matchup_obj,
				'tournament': tournament,
				'round_number': round_number
			})
	
	def post(self, request, tournament_id, round_number, matchup_number=None):
		matchup_id = request.POST.get("matchup_id")
		winner_id = request.POST.get("winner_id")
		loser_ids = request.POST.get("loser_ids")
		
		if loser_ids:
			loser_ids = loser_ids.split(',')[:-1]
		self.handler.process_tournament_matchup(request, matchup_id, winner_id, loser_ids)
		return redirect('tournament-matchup-actual', tournament_id=tournament_id, round_number=round_number)

class WinnerTournamentView(LoginRequiredMixin, WinnerPermissionMixin, View):
	helper_service = TournamentHelper()
	data_service = CompetitorGetData()

	def get(self, request, tournament_id):

		competitors = self.helper_service.get_competitors_info(self.tournament_obj, number=10)
		data = self.data_service.get_competitor_profile(self.competitor_obj)
		return render(request, 'frontend/tournaments/winner.html',
				{
					'data': data,
					'competitors': competitors,
					'tournament_id': tournament_id
				}
			)
