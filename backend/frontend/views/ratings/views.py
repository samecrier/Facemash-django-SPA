from django.views import View
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from services.ratings.service import LocalRatingService
from services.ratings.data_service import RatingData
from django.http import Http404


class RatingView(View):

	data_service = RatingData()
	def get(self, request):

		rating_type = request.GET.get('type')
		if rating_type not in('global', 'profile'):
			return redirect('/rating/?type=global')
		
		if rating_type == 'profile':
			try:
				data = self.data_service.get_data_top_ratingprofile(request.user, 300)
			except TypeError:
				raise Http404("Вы неавторизованны")
		elif rating_type == 'global':
			data = self.data_service.get_data_top_rating(300)

		competitors_data = [(competitor_id, data) for competitor_id, data in data.items()]
		competitor_paginator = Paginator(competitors_data, 20)
		page_number = request.GET.get('page', 1)
		competitors_page_obj = competitor_paginator.get_page(page_number)
		start_position = (competitors_page_obj.number - 1) * competitor_paginator.per_page
		return render(
			request,
			'frontend/ratings/rating.html', 
			{
				'competitors_page_obj': competitors_page_obj,
				'competitors_paginator': competitor_paginator,
				'start_position': start_position,
				'is_auth': request.user.is_authenticated,
			}
		)