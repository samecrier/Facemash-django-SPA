from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from services.ratings.service import LocalRatingService, APIRatingService
from services.matchups.helper import MatchupHelper, SavedMatchupHelper
from services.matchups.data_service import MatchupGetData, MatchupGetDataJS
from services.matchups.handler import MatchupHandler


class MatchupView(View):

	matchup_helper_service = MatchupHelper()
	saved_matchup_helper_service = SavedMatchupHelper()
	data_service = MatchupGetData()
	data_service_js = MatchupGetDataJS()

	def get(self, request):
		
		if request.user.is_authenticated:
			mode = request.GET.get('mode')
			if mode == 'refresh':
				competitor_1, competitor_2 = self.matchup_helper_service.get_two_competitors()
				updated_matchup = self.saved_matchup_helper_service.update_saved_matchup(
					request.user,
					competitor_1.id,
					'1',
					0,
					competitor_2.id
				)
				data = self.data_service.data_matchup(
						competitor_1_id=updated_matchup.competitor_1,
						competitor_2_id=updated_matchup.competitor_2,
						competitor_1_index=updated_matchup.competitor_1_ii,
						competitor_2_index=updated_matchup.competitor_2_ii,
					)
				return redirect('home')
			else:
				saved_matchup = self.saved_matchup_helper_service.get_saved_matchup(request)
				if saved_matchup:
					data = self.data_service.data_matchup(
						competitor_1_id=saved_matchup.competitor_1,
						competitor_2_id=saved_matchup.competitor_2,
						competitor_1_index=saved_matchup.competitor_1_ii,
						competitor_2_index=saved_matchup.competitor_2_ii,
					)
		else:
			
			winner_id = request.session.get("winner_id")
			winner_position = request.session.get("winner_position")
			winner_image_index = request.session.get("winner_image_index")
			enemy_id = request.session.get("enemy_id")
			enemy_1 = request.session.get("enemy_1")
			enemy_2 = request.session.get("enemy_2")

			if enemy_1 and enemy_2:
				data = self.data_service.data_matchup(
					competitor_1_id=enemy_1, 
					competitor_2_id=enemy_2
				)
			elif enemy_id:
				data = self.data_service.data_matchup(
					competitor_1_id=winner_id,
					competitor_2_id=enemy_id,
					competitor_1_index=winner_image_index,
					competitor_1_position=winner_position
				)
			# elif winner_id:
			# 	print('WINNER_ID')
			# 	data = self.data_service.get_data_enemy(winner_id, winner_position, winner_image_index)
			else:
				data = self.data_service.data_matchup(competitors=2)
				for i, competitor in enumerate(data):
					request.session[f'enemy_{i+1}'] = data[competitor]['competitor'].id
			if not enemy_id:
				for competitor in data:
					if winner_id:
						if int(winner_id) != data[competitor]["competitor"].id:
							request.session['enemy_id'] = data[competitor]['competitor'].id

		ratings = LocalRatingService.get_top_rating(20)
		
		return render(
			request, 
			'frontend/matchups/matchup.html',
			{
				'data': data,
				'ratings': ratings,
			}
		)
	
	def post(self, request):
		if request.headers.get('x-requested-with') == 'XMLHttpRequest':
			winner_id = request.POST.get("winner_id")
			loser_id = request.POST.get("loser_id")
			winner_position = request.POST.get("winner_position")
			winner_image_index = request.POST.get("winner_image_index")
			
			matchup_handler = MatchupHandler(request, winner_id, loser_id)
			matchup_handler.process_matchup()
			
			new_enemy = self.data_service_js.get_data_competitor_js(
				winner_id,
				loser_id,
				winner_position
			)

			for competitor in new_enemy:
				if int(winner_id) != new_enemy[competitor]["competitor"]['id']:
					enemy_id = new_enemy[competitor]['competitor']['id']
					if request.user.is_authenticated:
						self.saved_matchup_helper_service.update_saved_matchup(
							profile_id=request.user,
							winner_id=winner_id,
							winner_position=winner_position,
							winner_image_index=winner_image_index,
							enemy_id=enemy_id
						)
					else:
						request.session['enemy_id'] = enemy_id
			
			winner_rating = self.matchup_helper_service.get_winner_rating(winner_id)
			top_ratings = APIRatingService.get_top_rating(20)
			
			if not request.user.is_authenticated:
				request.session['winner_id'] = winner_id
				request.session['winner_position'] = winner_position
				request.session['winner_image_index'] = winner_image_index
				request.session['enemy_1'] = None
				request.session['enemy_2'] = None
			return JsonResponse({
				"status": "success",
				"loser_data": new_enemy,
				"winner_rating": winner_rating,
				"top_ratings": top_ratings
			})