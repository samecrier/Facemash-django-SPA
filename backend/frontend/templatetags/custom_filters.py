from django import template

register = template.Library()

@register.filter
def startswith(value, prefix):
	return value.startswith(prefix)

@register.filter
def last_dict_item(value):
	if isinstance(value, dict):
		return list(value.items())[-1]  # Возвращаем кортеж (key, value)
	return None