from niko.core.chatclient import ChatClient
from niko.core.dispatcher import Dispatcher

class NikoPlugin(ChatClient, Dispatcher):
	# Settings, Database, ChatClient, Scheduler
	is_plugin = True

	def reply(self, message, content):#, **kwargs):
		pass

	def say(self, username, content):#content, message=None, room=None, **kwargs):
		self.chat_client.say(username, content)


class PluginManager():
	pass