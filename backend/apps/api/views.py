from django.http import JsonResponse
from service.competitors.service import APICompetitorService

def get_competitor_api(request, competitor_id):
	# Получаем профиль
	competitor_service = APICompetitorService()
	data = competitor_service.get_competitor_data(competitor_id)
	# Формируем данные профиля
	return JsonResponse(data)