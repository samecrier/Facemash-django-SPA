from django.views import View
from django.shortcuts import render
from django.core.paginator import Paginator
from services.ratings_service import LocalRatingService


class RatingView(View):

	def get(self, request):
		competitors = LocalRatingService.get_top_rating(300)
		paginator = Paginator(competitors, 20)
		page_number = request.GET.get('page', 1)
		page_obj = paginator.get_page(page_number)
		return render(
			request,
			'frontend/rating.html', 
			{
				'page_obj': page_obj,
				'paginator': paginator
			}
		)