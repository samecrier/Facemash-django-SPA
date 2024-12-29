from django.db import connection
import logging
import time

logger = logging.getLogger(__name__)

class QueryCountMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Пропускаем запросы к favicon.ico
        if request.path == '/favicon.ico':
            return self.get_response(request)

        # Начало замера времени
        start_time = time.perf_counter()

        # Количество запросов до выполнения
        num_queries_before = len(connection.queries)

        # Обработка запроса
        response = self.get_response(request)

        # Количество запросов после выполнения
        num_queries_after = len(connection.queries)
        total_queries = num_queries_after - num_queries_before

        # Общее время выполнения SQL-запросов
        total_sql_time = sum(
            float(query.get('time', 0)) for query in connection.queries[num_queries_before:]
        )

        # Общее время загрузки страницы
        total_request_time = time.perf_counter() - start_time

        # Логирование результатов
        logger.info(f"_____________________________________________________")
        logger.info(f"Path: {request.path}")
        logger.info(f"Total SQL queries: {total_queries}")
        logger.info(f"Total SQL execution time: {total_sql_time:.2f} seconds")
        logger.info(f"Total request processing time: {total_request_time:.2f} seconds")
        logger.info(f"******************************************************")

        return response