from django.db.models.signals import post_delete
from django.dispatch import receiver
from service.matchups.service import LocalMatchupService
from apps.profiles.models import User
from django.contrib.auth.models import Group


# Автоматическая подстановка профиля
@receiver(post_delete, sender=User)
def replace_deleted_profile_with_guest(sender, profile_obj, **kwargs):
	guest_name = f"guest_{profile_obj.id}"
	
	# Ищем или создаём гостевой профиль
	guest_profile, created = User.objects.get_or_create(
		username=guest_name,
		defaults={
			'is_active': False,  # Неактивный профиль
			# Укажите другие поля, если нужно
		}
	)
	

	guest_group, _ = Group.objects.get_or_create(name='guest_archive')
	guest_profile.groups.add(guest_group)
	guest_profile.save()

	
	LocalMatchupService.update_profile_with_guest(profile_obj, guest_profile)