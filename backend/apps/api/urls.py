from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
	path('v01/competitor/<int:competitor_id>/', views.get_competitor_api, name='api-competitor'),
	path('v01/count-competitors/', views.count_competitors_api, name='api-count-competitors'),
	path('v01/calculate-participants/', views.calculate_participants, name='api-calculate-participants')
	
]