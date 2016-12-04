from niko.core.plugin import NikoPlugin
from niko.core.decorators import web, template

class WebPlugin(NikoPlugin):
	
	@web('/', method='GET')
	@template('home.html')
	def index(self):
		return {}


	@web('/user/:username', method='GET')
	@template('user.html')
	def user(self, username):
		return { 'username': username }