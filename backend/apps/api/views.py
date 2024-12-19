from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from services.competitors.service import APICompetitorService
import json
from apps.competitors.models import Competitor


def get_competitor_api(request, competitor_id):
	# Получаем профиль
	competitor_service = APICompetitorService()
	data = competitor_service.get_competitor_data(competitor_id)
	# Формируем данные профиля
	return JsonResponse(data)

@csrf_protect  # Убедитесь, что CSRF-защита включена
def count_competitors_api(request):
	if request.method == "POST":
		try:
			data = json.loads(request.body)
			city_ids = data.get('cities', [])
			print(f"CITY{city_ids}")
			count = Competitor.objects.filter(city__id__in=city_ids).count()
			return JsonResponse({'count': count}, status=200)
		except json.JSONDecodeError:
			return JsonResponse({'error': 'Invalid JSON'}, status=400)
	else:
		return JsonResponse({'error': 'Invalid request method'}, status=405)
	
@csrf_exempt  # Если не используете CSRF-токены (иначе удалите этот декоратор)
def calculate_participants(request):
	if request.method == 'POST':
		try:
			# Парсим данные из запроса
			data = json.loads(request.body)
			print(data)
			num_rounds = int(data.get('num_rounds', 0))
			num_per_matchup = int(data.get('num_per_matchup', 0))
			available_users = int(data.get('available_users', 0))

			# Выполняем расчёт
			calculated_participants = num_per_matchup ** num_rounds

			# Проверяем ограничения
			if calculated_participants > available_users:
				return JsonResponse({
					'error': f'Количество участников ({calculated_participants}) превышает доступное количество ({available_users}).'
				}, status=400)

			return JsonResponse({
				'calculated_participants': calculated_participants
			}, status=200)
		except (ValueError, json.JSONDecodeError):
			return JsonResponse({'error': 'Неверные данные.'}, status=400)

	return JsonResponse({'error': 'Метод запроса должен быть POST.'}, status=405)