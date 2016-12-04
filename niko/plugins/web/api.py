from niko.core.plugin import NikoPlugin
from niko.core.decorators import api, template
# from niko.core.statistics import 

class ApiPlugin(NikoPlugin):

	@api('/team/:team_id/mood/average/day', method='GET')
	def team_average_mood(self):
		return self.team_average_mood(10)

	@api('/team/:team_id/mood/average/day/:number_of_days', method='GET')
	def team_average_mood(self, number_of_days):
		return {}

	@api('/say/:message/to/:username')
	def talk(self, message, username):
		self.say(username, message)