from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
	path('v01/competitor/<int:competitor_id>/', views.get_competitor_api, name='api-competitor'),
]