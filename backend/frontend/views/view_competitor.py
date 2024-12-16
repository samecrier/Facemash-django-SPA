from django.shortcuts import render
from django.views import View
from frontend.helpers import GetData
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.core.paginator import Paginator


class CompetitorView(LoginRequiredMixin, TemplateView):

	home_helper = GetData()

	def get(self, request, competitor_id: int):
		data = self.home_helper.get_competitor_profile(competitor_id)
		matchups = data["matchups"]
		paginator = Paginator(matchups, 10)
		page_number = request.GET.get('page', 1)
		page_obj = paginator.get_page(page_number)
		return render(
			request, 
			'frontend/competitor.html', 
			{
				'data': data,
				'page_obj': page_obj,
			}
		)
	
