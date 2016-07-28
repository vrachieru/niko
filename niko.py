#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
import Skype4Py
import time
from datetime import datetime

database = "niko.db"

moods = {
	-2 : {
		"smileys" : [":'(", "(cry)"],
		"message" : "Oh no! Please go find a sympathetic ear. Or a hug"
	},
	-1 : {
		"smileys" : [":(", "(sad)"],
		"message" : "Sorry that things aren't going well! Go find a pick-me-up."
	},
	0 : {
		"smileys" : [":|"],
		"message" : "Alright, entry stored. Carry on with your meh self."
	},
	1 : {
		"smileys" : [":)"],
		"message" : "You're a joly fellow, aren't you?!"
	},
	2 : {
		"smileys" : [":D"],
		"message" : "Hei, sunshine! The database did a little dance recording this entry."
	}
}


class Niko(object):
	def __init__(self): 
		self.skype = Skype4Py.Skype(Events=self)
		self.skype.FriendlyName = "Niko"
		self.skype.Attach()
		
	def AttachmentStatus(self, status):
		if status == Skype4Py.apiAttachAvailable:
			self.skype.Attach()

	def SendReminder(self):
		for friend in self.skype.Friends:
			self.skype.SendMessage(friend.Handle, "Hei there little buddy. How's your day going?\n:D :) :| :( :'(")

	def MessageStatus(self, msg, status):
		if status == Skype4Py.cmsReceived:
			msg.MarkAsSeen()
			for mood, properties in moods.iteritems():
				if msg.Body in properties["smileys"]:
					userId = self.DbQuery("SELECT id from users where skype=?", (msg.Sender.Handle,))
					todaysDate = datetime.now().strftime("%Y-%m-%d")
					todaysMood = self.DbQuery("SELECT * from entries where userid=? and entry_date=?", (userId[0], todaysDate))
					if todaysMood == None:
						self.DbCommit("INSERT into entries (userid, mood, entry_date) VALUES (?, ?, ?)", (userId[0], mood, todaysDate))
					else:
						self.DbCommit("UPDATE entries SET mood=? WHERE id=?", (mood, todaysMood[0]))
					msg.Chat.SendMessage(properties["message"])
					return
			msg.Chat.SendMessage("Not quite what I'm looking for. Try one of the suggested smileys.")

	def DbQuery(self, query, args=()):
		connection = sqlite3.connect(database)
		cursor = connection.cursor()
		cursor.execute(query, args)
		return cursor.fetchone()

	def DbCommit(self, query, args=()):
		connection = sqlite3.connect(database)
		connection.cursor().execute(query, args)
		connection.commit()

if __name__ == "__main__":
	bot = Niko()
	today = datetime.now().isoweekday()

	while True:
		if datetime.now().isoweekday() != today and datetime.now().isoweekday() not in [6, 7] and datetime.now().strftime("%H") == "17":
			today = datetime.now().isoweekday()
			bot.SendReminder()
		time.sleep(1)