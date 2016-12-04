
import Skype4Py
from . import AbstractChatClient

from niko.core.dispatcher import Event
from niko.core.decorators import trigger


class Skype(AbstractChatClient):
	def __init__(self): 
		self.skype = Skype4Py.Skype(Events=self)
		self.skype.FriendlyName = "Niko"
		self.skype.Attach()

	def AttachmentStatus(self, status):
		if status == Skype4Py.apiAttachAvailable:
			self.skype.Attach()

	def Notify(self, notification):
		a, b = Skype4Py.utils.chop(notification)
		if a in ('CHAT'):
			object_type, object_id, prop_name, value = [a] + Skype4Py.utils.chop(b, 2)
			if object_type == 'CHAT':
				chat = self.skype.Chat(object_id)
				if prop_name == 'ACTIVITY_TIMESTAMP':
					message = chat.Messages[0]
					try:
						message.MarkAsSeen()
					except:
						pass
					self.received_message(message)

	@trigger(Event.CHAT_MESSAGE_NEW)
	def received_message(self, raw_message):
		return {
			'sender': {
				'nick': raw_message.Sender.Handle,
				'first_name': '',
				'last_name': ''
			},
			'message': raw_message.Body,
			'timestamp': ''
		}

	@trigger(Event.CHAT_CONTACT_NEW)
	def new_contact():
		pass

	@trigger(Event.CHAT_MESSAGE_NEW)
	def message_handler():
		pass

	def say(self, user, message):
		self.skype.SendMessage(user, message)

	def reply(self, message, content):
		pass

def bootstrap():
	return Skype()
