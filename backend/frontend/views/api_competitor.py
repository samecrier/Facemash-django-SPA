from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from services.competitors_service import APICompetitorService

def get_competitor_api(request, competitor_id):
	# Получаем профиль
	competitor_service = APICompetitorService()
	data = competitor_service.get_competitor_data(competitor_id)
	# Формируем данные профиля
	return JsonResponse(data)