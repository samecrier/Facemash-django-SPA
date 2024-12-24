from django import forms
from apps.competitors.models import Location

class TournamentSelectionForm(forms.Form):
	cities = forms.ModelMultipleChoiceField(
		queryset=Location.objects.all(),
		widget=forms.CheckboxSelectMultiple,
		label="Выберите города",
		required = True,
		error_messages={
			'required': "Пожалуйста, выберите хотя бы один город.",  # Изменяем текст ошибки
		}
	)

	# Поля для ввода данных
	num_participants = forms.CharField(
		label="Участников",
		required=True,
		widget=forms.NumberInput(attrs={"readonly": "readonly"}),
		error_messages={'required': "Укажите количество участников."}
	)
	num_rounds = forms.CharField(
		label="Раундов",
		required=True,
		error_messages={'required': "Укажите количество раундов."}
	)
	num_per_matchup = forms.CharField(
		label="В одном матчапе",
		required=True,
		error_messages={'required': "Укажите количество участников в одном матчапе."}
	)