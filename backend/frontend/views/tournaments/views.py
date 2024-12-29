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
from pprint import pprint


class HomeTournamentView(LoginRequiredMixin, View):
	data_service = TournamentGetData()
	
	def get(self, request):
		profile_obj = request.user
		data = self.data_service.get_tournaments_base(profile_obj)
		return render(request, 'frontend/tournaments/main.html',
			{'data': data}
		)


class CreateTournamentView(LoginRequiredMixin, View):
	helper_service = TournamentHelper()
	handler_service = TournamentHandler()
	
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
	data_service = TournamentGetData()
	
	def get(self, request, tournament_id):
		data = self.data_service.get_tournament_info_by_obj(self.tournament_obj)
		competitors = [(competitor, data) for competitor, data in data['tournament_competitors'].items()]
		competitors_paginator = Paginator(competitors, 20)
		page_number = request.GET.get('page', 1)
		competitors_page = competitors_paginator.get_page(page_number)
		return render(request, 'frontend/tournaments/info.html', {
			'competitors_page': competitors_page,
			'competitors_paginator': competitors_paginator,
			'data': data,
		})


class StageTournamentView(LoginRequiredMixin, RoundPermissionMixin, View):
	helper_service = TournamentHelper()
	data_service = TournamentGetData()
	
	def get(self, request, tournament_id, round_number):
		
		matchups = self.helper_service.get_stage_matchups(self.round_obj)
		stage_data = self.data_service.get_data_stage(request, matchups)
		return render(request, 'frontend/tournaments/stage.html',
			{
				'stage_data': stage_data
			})


class MatchupTournamentView(LoginRequiredMixin, MatchupPermissionMixin, View):
	helper_service = TournamentHelper()
	matchup_data_service = MatchupGetData()
	tournament_data_service = TournamentGetData()
	handler=TournamentHandler()

	def get(self, request, tournament_id, round_number, matchup_number=None):
		
		competitors = self.matchup_data_service.data_matchup(**self.competitors_in_matchup)
		matchup_data = self.tournament_data_service.get_matchup_info_by_obj(self.matchup_obj)
		return render(request, 'frontend/tournaments/tournament_matchup.html',
			{	
				'matchup_data': matchup_data,
				'competitors': competitors,
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
	tournament_data_service = TournamentGetData()
	competitor_data_service = CompetitorGetData()

	def get(self, request, tournament_id):

		data_competitor = self.competitor_data_service.get_competitor_profile(self.competitor_obj)
		return render(request, 'frontend/tournaments/winner.html',
				{
					'data_competitor': data_competitor,
					'tournament_id': tournament_id
				}
			)

