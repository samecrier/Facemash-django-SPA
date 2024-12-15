from django.core.management.base import BaseCommand
from profiles.models import User
from django.contrib.auth.models import Group

class Command(BaseCommand):
	help = "Создает группы пользователей: guest, user, admin."

	def handle(self, *args, **kwargs):
		groups = ['user', 'superuser', 'admin', 'guest']

		for group_name in groups:
			group, created = Group.objects.get_or_create(name=group_name)
			if created:
				self.stdout.write(self.style.SUCCESS(f"Группа '{group_name}' успешно создана."))
			else:
				self.stdout.write(self.style.WARNING(f"Группа '{group_name}' уже существует."))

		for user in ['saycry', 'samecrier', 'guest', 'saveliar']:
			if user == 'samecrier':
				user = User.objects.get(username=user)
				group = Group.objects.get(name="superuser")
				user.groups.add(group)
				user.save()
			elif user == 'saycry':
				user = User.objects.get(username=user)
				group = Group.objects.get(name="admin")
				user.groups.add(group)
				user.save()
			elif user == 'saveliar':
				user = User.objects.get(username=user)
				group = Group.objects.get(name="user")
				user.groups.add(group)
				user.save()
			elif user == 'guest':
				user = User.objects.get(username=user)
				group = Group.objects.get(name="guest")
				user.groups.add(group)
				user.save()
