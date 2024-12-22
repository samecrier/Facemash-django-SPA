from django.http import HttpResponse
from django.urls import reverse
from django.views import View
from django.shortcuts import render, redirect
from apps.competitors.forms import CitySelectionForm
from services.competitors.service import LocalCompetitorService
from services.matchups.data_service import MatchupGetData
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
		actual_round = self.helper_service.get_actual_round_obj_by_tournament_string(tournament_id)
		if not actual_round:
			return redirect('tournament-winner', tournament_id)
		paginator = Paginator(competitors, 20)
		page_number = request.GET.get('page', 1)
		page_obj = paginator.get_page(page_number)
		start_position = (page_obj.number - 1) * paginator.per_page
		return render(request, 'frontend/tournaments/info.html', {
			'page_obj': page_obj,
			'paginator': paginator,
			'start_position': start_position,
			'actual_round': actual_round,
		})

class StageTournamentView(View):
	helper_service = TournamentHelper()

	def get(self, request, tournament_id, round_number):
		actual_round = self.helper_service.get_certain_round_obj(tournament_id, round_number)
		generate_matchups = self.helper_service.get_actual_matchups(actual_round)
		return render(request, 'frontend/tournaments/stage.html', {'actual_round':actual_round})
		# matchups = self.helper_service.get_actual_matchup(actual_round)


class MatchupTournamentView(View):
	helper_service = TournamentHelper()
	data_service = MatchupGetData()
	handler=TournamentHandler()
	def get(self, request, tournament_id, round_number, matchup_number=None):
		if not matchup_number:
			competitors_in_matchup, matchup_obj = self.helper_service.get_actual_matchup(tournament_id, round_number)
			if not matchup_obj:
				next_round_number = self.helper_service.turn_next_round(tournament_id, round_number)
				if not next_round_number:
					return redirect('tournament-winner', tournament_id)
				return redirect('tournament-stage', tournament_id, next_round_number)
			data = self.data_service.data_matchup(**competitors_in_matchup)
			return render(request, 'frontend/tournaments/tournament_matchup.html',
				{
					'data': data,
					'matchup': matchup_obj,
				})
		
	def post(self, request, tournament_id, round_number, matchup_number=None):
		matchup_id = request.POST.get("matchup_id")
		winner_id = request.POST.get("winner_id")
		loser_ids = request.POST.get("loser_ids")
		
		if loser_ids:
			loser_ids = loser_ids.split(',')[:-1]
		self.handler.process_tournament_matchup(request, matchup_id, winner_id, loser_ids)
		return redirect('tournament-matchup-actual', tournament_id=tournament_id, round_number=round_number)

class WinnerTournamentView(View):
	helper_service = TournamentHelper()
	
	def get(self, request, tournament_id):
		winner = self.helper_service.get_winner(tournament_id)
		return render(request, 'frontend/tournaments/winner.html',
				{'winner': winner}
			)
