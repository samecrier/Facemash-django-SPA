from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
	help = "Создает группы пользователей: guest, user, admin."

	def handle(self, *args, **kwargs):
		groups = ['user', 'superuser', 'admin']

		for group_name in groups:
			group, created = Group.objects.get_or_create(name=group_name)
			if created:
				self.stdout.write(self.style.SUCCESS(f"Группа '{group_name}' успешно создана."))
			else:
				self.stdout.write(self.style.WARNING(f"Группа '{group_name}' уже существует."))
