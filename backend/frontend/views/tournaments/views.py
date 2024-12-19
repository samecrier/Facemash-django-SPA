from django.http import HttpResponse
from django.urls import reverse
from django.views import View
from django.shortcuts import render, redirect
from apps.competitors.forms import CitySelectionForm
from services.competitors.service import LocalCompetitorService
from services.tournaments.data_service import TournamentGetData
from services.tournaments.helper import TournamentHelper
from services.tournaments.handler import TournamentHandler
from django.core.paginator import Paginator

class HomeTournamentView(View):
	
	helper_service = TournamentHelper()
	
	def get(self, request):
		tournaments = self.helper_service.get_tournaments_base()
		return render(request, 'frontend/tournaments/main.html',
			{'tournaments': tournaments})


class CreateTournamentView(View):
	
	competitor_service = LocalCompetitorService()
	handler_service = TournamentHandler()
	data_service = TournamentGetData()
	
	def get(self, request):
		location_form = CitySelectionForm()
		return render(request, 'frontend/tournaments/create.html', {'location_form': location_form})
	
	def post(self, request):
		location_form = CitySelectionForm(request.POST)  # Заполняем форму данными POST
		if location_form.is_valid():  # Проверяем валидацию
			# Получаем выбранные города
			cities = location_form.cleaned_data['cities']
			participants = location_form.cleaned_data['num_participants']
			rounds = location_form.cleaned_data['num_rounds']
			in_matchup = location_form.cleaned_data['num_per_matchup']
			self.handler_service.process_tournament(request, cities, participants, rounds, in_matchup)
			return redirect(reverse('tournament-create'))  # Редирект при успешной обработке
		else:
			# Возвращаем форму с ошибками
			return render(request, 'frontend/tournaments/create.html', {'location_form': location_form})


class ConfirmationCreateTournamentView(View):
	
	def get(self, request, tournament_id):
		pass


class TournamentView(View):
	helper_service = TournamentHelper()
	
	def get(self, request, tournament_id):
		competitors = self.helper_service.get_competitors_info(tournament_id)

		paginator = Paginator(competitors, 20)
		page_number = request.GET.get('page', 1)
		page_obj = paginator.get_page(page_number)
		start_position = (page_obj.number - 1) * paginator.per_page
		return render(request, 'frontend/tournaments/info.html', {
			'page_obj': page_obj,
			'paginator': paginator,
			'start_position': start_position,
		})


class MatchupTournamentView(View):

	def get(self, request, tournament_id, round_id, matchup_id):
		pass


class StageTournamentView(View):
	
	def get(self, request, tournament_id, round_id):
		pass


class WinnerTournamentView(View):
	
	def get(self, request, tournament_id):
		pass