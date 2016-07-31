from utils import timestamp

class Logger():
	def info(self, message):
		self.write('info', message)

	def warn(self, message):
		self.write('warn', message)

	def err(self, message):
		self.write('err', message)

	def write(self, level, message):
		entry = '%s [%s] %s' % (timestamp(), level, message)
		print (entry)
		log = open('application.log','a+')
		log.write('%s\n' % entry)
		log.close()

LOGGER = Logger()