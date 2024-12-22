from django.db import connection
import logging

logger = logging.getLogger(__name__)

class QueryCountMiddleware:
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		# До обработки запроса
		num_queries_before = len(connection.queries)

		response = self.get_response(request)

		# После обработки запроса
		num_queries_after = len(connection.queries)
		total_queries = num_queries_after - num_queries_before

		# Логируем количество запросов
		logger.info(f"_____________________________________________________")
		logger.info(f"Total SQL queries for {request.path}: {total_queries}")
		logger.info(f"_____________________________________________________")

		return response
