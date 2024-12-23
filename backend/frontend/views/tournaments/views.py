from django.http import HttpResponse, Http404
from django.db import transaction
from django.urls import reverse
from django.views import View
from django.shortcuts import render, redirect
from apps.competitors.forms import CitySelectionForm
from services.competitors.service import LocalCompetitorService
from services.tournaments.service import LocalTournamentService
from services.matchups.data_service import MatchupGetData
from services.tournaments.data_service import TournamentGetData
from services.tournaments.helper import TournamentHelper
from services.tournaments.handler import TournamentHandler
from django.core.paginator import Paginator

class HomeTournamentView(View):
	
	helper_service = TournamentHelper()
	
	def get(self, request):
		data = self.helper_service.get_tournaments_base()
		return render(request, 'frontend/tournaments/main.html',
			{'data': data}
		)


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
			tournament_id, round_number = self.handler_service.process_tournament(request, cities, participants, rounds, in_matchup)
			return redirect('tournament-stage', tournament_id, round_number) # Редирект при успешной обработке
		else:
			# Возвращаем форму с ошибками
			return render(request, 'frontend/tournaments/create.html', {'location_form': location_form})


class TournamentView(View):
	helper_service = TournamentHelper()
	
	def get(self, request, tournament_id):
		competitors = self.helper_service.get_competitors_info(tournament_id)
		actual_rounds_status = self.helper_service.actual_rounds_status(tournament_id)
		tournament_obj = self.helper_service.get_tournament_obj(tournament_id)
		actual_round = self.helper_service.get_actual_round_obj_by_tournament(tournament_id)
		paginator = Paginator(competitors, 20)
		page_number = request.GET.get('page', 1)
		page_obj = paginator.get_page(page_number)
		start_position = (page_obj.number - 1) * paginator.per_page
		return render(request, 'frontend/tournaments/info.html', {
			'page_obj': page_obj,
			'paginator': paginator,
			'start_position': start_position,
			'tournament_obj': tournament_obj,
			'actual_round': actual_round,
			'actual_rounds_status': actual_rounds_status
		})

class StageTournamentView(View):
	helper_service = TournamentHelper()
	data_service = TournamentGetData()
	tournament_service = LocalTournamentService()
	
	def get(self, request, tournament_id, round_number):
		tournament_obj = self.tournament_service.get_tournament_obj(tournament_id)
		if not tournament_obj:
			raise Http404("Такого турнира не существует")
		
		actual_round = self.tournament_service.get_round_obj_by_tournament_obj(tournament_obj, round_number)
		if not actual_round:
			raise Http404("Такого раунда не существует")
		
		matchups = self.helper_service.get_stage_matchups(actual_round)
		if not matchups:
			raise Http404("Раунд еще не инициализирован")
		

		data = self.data_service.get_data_stage(request, matchups)
		return render(request, 'frontend/tournaments/stage.html',
			{
				'data': data
			})


class MatchupTournamentView(View):
	helper_service = TournamentHelper()
	data_service = MatchupGetData()
	handler=TournamentHandler()
	tournament_service = LocalTournamentService()

	def get(self, request, tournament_id, round_number, matchup_number=None):
		tournament_obj = self.tournament_service.get_tournament_obj(tournament_id)
		tournament = {
			'id': tournament_obj.id,
			'winner_id': tournament_obj.winner_id,
		}
		if not tournament_obj:
			raise Http404("Такого турнира не существует")
		
		round_obj = self.tournament_service.get_round_obj_by_tournament_obj(tournament_obj, round_number)
		if not round_obj:
			raise Http404("Такого раунда не существует")
		if not round_obj:
			raise Http404("Такого раунда или турнира не существует")
		actuality = self.helper_service.check_actuality_round_obj(tournament_obj, round_obj)
		if not actuality:
			raise Http404("Этот раунд еще не инициализирован")

		competitors_in_matchup, matchup_obj = self.helper_service.get_actual_matchup(round_obj, matchup_number)
		if not matchup_obj:
			if matchup_number:
				raise Http404("Такого номера матчапа не существует")
			else:
				next_round_number = self.helper_service.turn_next_round(tournament_id, round_number)
				if not next_round_number:
					return redirect('tournament-winner', tournament_id)
				return redirect('tournament-stage', tournament_id, next_round_number)
		
		matchups_count = self.helper_service.get_count_matchup_in_round(tournament_id, round_number)
		data = self.data_service.data_matchup(**competitors_in_matchup)
		return render(request, 'frontend/tournaments/tournament_matchup.html',
			{	
				'matchups_count': matchups_count,
				'data': data,
				'matchup': matchup_obj,
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

class WinnerTournamentView(View):
	helper_service = TournamentHelper()
	
	def get(self, request, tournament_id):
		winner = self.helper_service.get_winner(tournament_id)
		return render(request, 'frontend/tournaments/winner.html',
				{'winner': winner}
			)
