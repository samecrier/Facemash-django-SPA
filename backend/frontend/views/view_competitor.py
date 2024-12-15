from django.shortcuts import render
from django.views import View
from frontend.helpers import GetData
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class CompetitorView(LoginRequiredMixin, TemplateView):

	home_helper = GetData()

	def get(self, request, competitor_id: int):
		data = self.home_helper.get_competitor_profile(competitor_id)
		return render(
			request, 
			'frontend/competitor.html', 
			{'data': data}
		)
	
