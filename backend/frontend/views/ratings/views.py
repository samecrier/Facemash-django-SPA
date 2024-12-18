from django.views import View
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from services.ratings.service import LocalRatingService
from django.http import Http404


class RatingView(View):

	def get(self, request):

		rating_type = request.GET.get('type')
		if rating_type not in('global', 'profile'):
			return redirect('/rating/?type=global')
		
		if rating_type == 'profile':
			try:
				competitors = LocalRatingService.get_top_ratingprofile(request.user, 300)
			except TypeError:
				raise Http404("Вы неавторизованны")
		elif rating_type == 'global':
			competitors = LocalRatingService.get_top_rating(300)

		paginator = Paginator(competitors, 20)
		page_number = request.GET.get('page', 1)
		page_obj = paginator.get_page(page_number)
		start_position = (page_obj.number - 1) * paginator.per_page
		return render(
			request,
			'frontend/ratings/rating.html', 
			{
				'page_obj': page_obj,
				'paginator': paginator,
				'start_position': start_position,
				'is_auth': request.user.is_authenticated,
			}
		)