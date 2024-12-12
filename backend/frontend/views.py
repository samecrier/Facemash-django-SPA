from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from services.competitors_service import LocalCompetitorService
from services.ratings_service import LocalRatingService
from frontend.helpers import GetData
from frontend.handlers import MatchupHandler
import json


class HomeView(View):

	def get(self, request):
		winner_id = request.session.get("winner_id")
		winner_position = request.session.get("winner_position")
		winner_image_index = request.session.get("winner_image_index")
		
		home_helper = GetData()
		if winner_id:
			data = home_helper.get_enemy(winner_id, winner_position, winner_image_index)
		else:
			data = home_helper.get_data_competitors(2)
		
		ratings = LocalRatingService.get_top_rating()
		
		return render(
			request, 
			'frontend/index.html',
			{
				'data': data,
				'ratings': ratings,
			}
		)
	
	def post(self, request):
		winner_id = request.POST.get("winner_id")
		loser_id = request.POST.get("loser_id")
		print(f"WINNER{winner_id}, {loser_id}")
		winner_position = request.POST.get("winner_position")
		winner_image_index = request.POST.get("winner_image_index")
		
		matchup_handler = MatchupHandler(winner_id, loser_id)
		matchup_handler.process_matchup()

		request.session['winner_id'] = winner_id
		request.session['loser_id'] = loser_id
		request.session['winner_position'] = winner_position
		request.session['winner_image_index'] = winner_image_index
		return redirect("home")