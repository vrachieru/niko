#!/usr/bin/python
# -*- coding: utf-8 -*-

import Skype4Py
import time

from config import *
from database import *
from log import *
from scheduler import *
from status import *
from utils import *

SMILEYS = ':D :) :| :( :\'('
REMINDER = 'Hei there little buddy. How\'s your day going?\n%s' % SMILEYS
USER_NOT_FOUND = 'You\'re not on the list. Back of the line buster!'
INVALID_RESPONSE = 'I\'m not quite sure what vibe I\'m getting. Try one of these: %s' % SMILEYS

class Niko(object):
	def __init__(self): 
		self.skype = Skype4Py.Skype(Events=self)
		self.skype.FriendlyName = "Niko"
		self.skype.Attach()
		
	def AttachmentStatus(self, status):
		if status == Skype4Py.apiAttachAvailable:
			self.skype.Attach()

	def SendMessageToAll(self, message):
		LOGGER.info('Sending message to all users: %s' % message)
		for friend in self.skype.Friends:
			self.skype.SendMessage(friend.Handle, message)

	def MessageStatus(self, message, status):
		if status == Skype4Py.cmsReceived:
			message.MarkAsSeen()
			self.Message(message)

	def Message(self, message):
		LOGGER.info('Received message from %s: %s' % (message.Sender.Handle, message.Body))
		user = findUserBySkypeId(message.Sender.Handle)
		if user == None:
			message.Chat.SendMessage(USER_NOT_FOUND)
			LOGGER.warn('%s is not registered in the database' % message.Sender.Handle)
			return

		mood = getMoodBySmiley(message.Body)
		if mood != None:
			setUserMood(user, mood)
			LOGGER.info('%s is %s today' % (message.Sender.Handle, mood['smileys'][0]))
			reply = getRandomItem(mood['messages'])
			message.Chat.SendMessage(reply)
			LOGGER.info('Sent reply to %s: %s' % (message.Sender.Handle, reply))
			return
		
		message.Chat.SendMessage(INVALID_RESPONSE)
		LOGGER.warn('Gibberish received from %s: %s' % (message.Sender.Handle, message.Body))


if __name__ == "__main__":
	niko = Niko()

	scheduler \
		.every() \
		.workday() \
		.at(SCHEDULERS['reminder']) \
		.do(niko.SendMessageToAll, REMINDER)

	scheduler \
		.every() \
		.workday() \
		.at(SCHEDULERS['yesterdaysMood']) \
		.do(niko.SendMessageToAll, getYesterdaysMood())

	while True:
		scheduler.run_jobs()
		time.sleep(1.0)
