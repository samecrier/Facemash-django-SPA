from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.conf import settings
from django.utils.safestring import mark_safe
from services.competitors_service import LocalCompetitorService
import json

def home(request):
	competitor_service = LocalCompetitorService()
	competitors = []
	first_competitor = competitor_service.get_random_competitor()
	competitors.append(first_competitor)
	while True:
		second_competitor = competitor_service.get_random_competitor()
		if second_competitor != first_competitor:
			competitors.append(second_competitor)
			break
	first_images = first_competitor.images.all()
	second_images = second_competitor.images.all()

	return render(
		request, 
		'frontend/index.html',
		{
			'competitors': competitors,

			'initial_image_1': first_images[0].get_path(),
			'image_count_1': first_images.count(),
			'other_images_1': mark_safe(json.dumps([image.get_path() for image in first_images[1:]])),

			'initial_image_2': second_images[0].get_path(),
			'image_count_2': second_images.count(),
			'other_images_2': mark_safe(json.dumps([image.get_path() for image in second_images[1:]])),
		}
	)
