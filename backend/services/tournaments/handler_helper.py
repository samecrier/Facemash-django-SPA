from random import sample

class HandlerHelper():

	@staticmethod
	def choose_random_competitors(
		competitors_list, participants):
		competitors_list = list(competitors_list)
		participants = int(participants)
		participants_list = sample(competitors_list, participants)
		return participants_list
