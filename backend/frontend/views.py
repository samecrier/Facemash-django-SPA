from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from services.competitors_service import LocalCompetitorService
from frontend.helpers import GetData
import json


class HomeView(View):

	def get(self, request):
		winner_id = request.session.get("winner_id")
		winner_position = request.session.get("winner_position")
		current_image_index = request.session.get("current_image_index")
		
		home_service = GetData()
		if winner_id:
			data = home_service.get_enemy(2, winner_id, winner_position, current_image_index)
		else:
			data = home_service.get_data_competitors(2)

		return render(
			request, 
			'frontend/index.html',
			{'data': data}
		)
	
	def post(self, request):
		winner_id = request.POST.get("winner_id")
		winner_position = request.POST.get("winner_position")
		current_image_index = request.POST.get("image_index")
		loser_ids = [competitor_id for competitor_id in request.POST.get("loser_ids").split(',') 
			if competitor_id != '']
		request.session['winner_id'] = winner_id
		request.session['winner_position'] = winner_position
		request.session['current_image_index'] = current_image_index
		return redirect("home")