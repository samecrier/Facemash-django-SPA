from django.core.management.base import BaseCommand
from profiles.models import User

class Command(BaseCommand):
	help = "Создает группы пользователей: guest, user, admin."

	def handle(self, *args, **kwargs):
		
		user, created = User.objects.get_or_create(username='saycry')
		if created:
			user.set_unusable_password()  # Делает пароль нерабочим
			user.save()