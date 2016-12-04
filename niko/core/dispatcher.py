from cache import Cache


class Event():
	CHAT_MESSAGE_NEW = 'chat.message.new'
	CHAT_CONTACT_NEW = 'chat.contact.new'

class Listener():
	pass

class Dispatcher(Cache):
	@property
	def dispatcher(self):
		if not hasattr(self, 'dispatcher'):
			self.dispatcher = ObserverThingy()
		return self.dispatcher



class ObserverThingy():

	def __init__(self):
		self.handlers = {}

	def handler(self, event): # on
		event = event.__func__
		def register_handler(fun):
			if not event in self.handlers:
				self.handlers[event] = []
			self.handlers[event].append(fun)
			return fun
		return register_handler

	def event(self, fun): # trigger
		def wrapper(*args, **kwargs):
			for handler in self.handlers[fun]:
				# if regex satisfied
				handler(*args, **kwargs)
			return fun(*args, **kwargs)
		wrapper.__func__ = fun
		return wrapper