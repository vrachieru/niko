from abc import ABCMeta, abstractmethod
from importlib import import_module
import time

from niko.core.decorators import trigger

class AbstractChatClient():
	__metaclass__ = ABCMeta

	@trigger
	@abstractmethod
	def received_message(self, message):
		'''Message received'''
		pass

	@abstractmethod
	def say(self, username, content):
		'''Sends a message'''
		pass

	@abstractmethod
	def reply(self, message, content):
		'''Replies to a message'''
		pass


class ChatClient(object):
	def bootstrap_chatclient(self):
		self.chat_client

		while True:
			time.sleep(100)

	@property
	def chat_client(self):
		if not hasattr(self, 'chatclient'):
			module_name = 'niko.core.chatclient.skype'
			chat_module = import_module(module_name)
			self.chatclient = chat_module.bootstrap()
		return self.chatclient