from django.db import transaction
from django.db.models import QuerySet, Q
from abc import ABC, abstractmethod
from apps.profiles.models import User
from typing import List


class ProfileService(ABC):

	@abstractmethod
	def get_guest_profile(self, *args, **kwargs):
		pass


class LocalProfileService(ProfileService):
	
	def get_guest_profile(self):
		return User.objects.get(username='guest')

class APIProfileService(ProfileService):
	pass
