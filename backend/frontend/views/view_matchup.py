from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from services.ratings_service import LocalRatingService, APIRatingService
from frontend.helpers import GetData
from frontend.handlers import MatchupHandler


class HomeView(View):

	home_helper = GetData()

	def get(self, request):
		
		if request.user.is_authenticated:
			mode = request.GET.get('mode')
			if mode == 'refresh':
				competitor_1, competitor_2 = self.home_helper.get_two_competitors()
				updated_matchup = self.home_helper.update_saved_matchup(
					request.user,
					competitor_1.id,
					'1',
					0,
					competitor_2.id
				)
				data = self.home_helper.get_saved_data(
						updated_matchup.competitor_1,
						updated_matchup.competitor_2,
						updated_matchup.competitor_1_ii,
						updated_matchup.competitor_2_ii,
					)
				return redirect('home')
			else:
				saved_matchup = self.home_helper.get_saved_matchup(request)
				if saved_matchup:
					data = self.home_helper.get_saved_data(
						saved_matchup.competitor_1,
						saved_matchup.competitor_2,
						saved_matchup.competitor_1_ii,
						saved_matchup.competitor_2_ii,
					)
		else:
			
			winner_id = request.session.get("winner_id")
			winner_position = request.session.get("winner_position")
			winner_image_index = request.session.get("winner_image_index")
			enemy_id = request.session.get("enemy_id")
			enemy_1 = request.session.get("enemy_1")
			enemy_2 = request.session.get("enemy_2")

			if enemy_1 and enemy_2:
				print('ENEMY_1 ENEMY_2')
				data = self.home_helper.get_specific_matchup(enemy_1, enemy_2)
			elif enemy_id:
				print('ENEMY_ID')
				data = self.home_helper.get_specific_matchup_guest(winner_id, winner_position, winner_image_index, enemy_id)
			# elif winner_id:
			# 	print('WINNER_ID')
			# 	data = self.home_helper.get_enemy(winner_id, winner_position, winner_image_index)
			else:
				print('ELSE')
				data = self.home_helper.get_data_competitors(2)
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
			'frontend/matchup.html',
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
			
			new_enemy = self.home_helper.get_competitor_js(
				winner_id,
				loser_id,
				winner_position
			)

			for competitor in new_enemy:
				if int(winner_id) != new_enemy[competitor]["competitor"]['id']:
					enemy_id = new_enemy[competitor]['competitor']['id']
					if request.user.is_authenticated:
						self.home_helper.update_saved_matchup(
							profile_id=request.user,
							winner_id=winner_id,
							winner_position=winner_position,
							winner_image_index=winner_image_index,
							enemy_id=enemy_id
						)
					else:
						request.session['enemy_id'] = enemy_id
			
			winner_rating = self.home_helper.get_winner_rating(winner_id)
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