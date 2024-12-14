from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from services.ratings_service import LocalRatingService, APIRatingService
from frontend.helpers import GetData
from frontend.handlers import MatchupHandler


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
			'frontend/indexhtml.html',
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

		return redirect("home-archieve")


class HomeViewJS(View):

	home_helper = GetData()

	def get(self, request):
		winner_id = request.session.get("winner_id")
		winner_position = request.session.get("winner_position")
		winner_image_index = request.session.get("winner_image_index")
		
		
		if winner_id:
			data = self.home_helper.get_enemy(winner_id, winner_position, winner_image_index)
		else:
			data = self.home_helper.get_data_competitors(2)
		
		ratings = LocalRatingService.get_top_rating(20)
		
		return render(
			request, 
			'frontend/matchup.html',
			{
				'data': data,
				'ratings': ratings,
			}
		)
	
	def post(self, request):
		print('я тут')
		if request.headers.get('x-requested-with') == 'XMLHttpRequest':
			winner_id = request.POST.get("winner_id")
			loser_id = request.POST.get("loser_id")
			print(f"WINNER{winner_id}, {loser_id}")
			winner_position = request.POST.get("winner_position")
			winner_image_index = request.POST.get("winner_image_index")
			
			matchup_handler = MatchupHandler(winner_id, loser_id)
			matchup_handler.process_matchup()
			
			new_loser = self.home_helper.get_competitor_js(
				winner_id,
				loser_id,
				winner_position
			)

			winner_rating = self.home_helper.get_winner_rating(winner_id)
			top_ratings = APIRatingService.get_top_rating(20)
			
			request.session['winner_id'] = winner_id
			request.session['loser_id'] = loser_id
			request.session['winner_position'] = winner_position
			request.session['winner_image_index'] = winner_image_index
			return JsonResponse({
				"status": "success",
				"loser_data": new_loser,
				"winner_rating": winner_rating,
				"top_ratings": top_ratings
			})