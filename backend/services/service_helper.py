class StringHelper:
	
	@staticmethod
	def get_obj_by_string(model, model_id):
		return model.objects.filter(id=model_id).first()