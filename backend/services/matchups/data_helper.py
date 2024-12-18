from collections import defaultdict

class DataHelper():
	
	@staticmethod
	def dict_from_params(data):
		"""
		Превращает параметры из kwargs обрабатывая _position _index _x params
		в dict для дальнешей обработки

		:param data: dict
		return dict
		"""
		result = {}
		for key, value in data.items():
			try:
				parts = key.rsplit("_", 1)  # Разделить на две части, начиная с конца
				main_key, sub_key = parts[0], parts[1]
				
				# Вложенный словарь с ключом main_key
				if main_key not in result:
					result[main_key] = {}
				
				if isinstance(value, (str, int)):
					result[main_key][sub_key] = int(value)
				else:
					result[main_key][sub_key] = value
			except IndexError:
				pass
		return result
	
	@staticmethod
	def generate_params_matchup(raw_data_key):
		"""
		Генерирует dict вставляя данные в такой шаблон по ключам из kwargs
		{'id': None,
		'index': None,
		'position': None}

		:param raw_data_key: dict
		return dict
		"""
		data = {
			'id': None,
			'index': None,
			'position': None
		}
		for key, value in raw_data_key.items():
			data[key] = value
		return data
	
	@staticmethod
	def get_data_matchup(template_data):
		"""
		Возвращает dict в готовом порядке, определенными индексами и позициями,
		где key это 1,2,3...итд

		:params template_data: dict
		return dict
		"""
		data = defaultdict(dict)
		position_slots = [template_data[key]['position'] for key in template_data]
		filtered_positions = [pos for pos in position_slots if pos is not None]
		if len(filtered_positions) != len(set(filtered_positions)):
			raise ValueError(f"Ошибка: имеются повторяющиеся позиции {filtered_positions}")
		range_position = [i for i in range(1, len(template_data)+1)]
		for i_competitor in template_data:

			if template_data[i_competitor]['position']:
				if template_data[i_competitor]['position'] > len(template_data):
					raise ValueError(f"{i_competitor} имеет позицию {template_data[i_competitor]['position']}, что превышает длину {len(template_data)}")
				position = template_data[i_competitor]['position']
			else:
				for position_index in range_position:
					if position_index not in filtered_positions:
						none_index = position_slots.index(None)
						position = position_index
						position_slots[none_index] = position_index
						filtered_positions.append(position_index)
						break
			
			if not template_data[i_competitor]['id']:
				raise ValueError(f"Ошибка: передался id=None для competitor-{i_competitor}")
			data[position]['id'] = template_data[i_competitor]['id']
			if template_data[i_competitor]['index']:
				data[position]['index'] = template_data[i_competitor]['index']
			else:
				data[position]['index'] = 0
		
		data = dict(data)
		return data