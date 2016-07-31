import sqlite3
from collections import namedtuple

from config import *
from utils import *

Team = namedtuple('Team',  ['id', 'name'])
User = namedtuple('User',  ['id', 'username', 'password', 'skype', 'team'])
Entry = namedtuple('Entry', ['id', 'userid', 'mood', 'entry_date'])


def executeScript(script):
	connection = sqlite3.connect(DATABASE_FILE)
	cursor = connection.cursor()
	cursor.executescript(script)
	connection.commit()

def executeQuery(query, args=()):
	connection = sqlite3.connect(DATABASE_FILE)
	cursor = connection.cursor()
	cursor.execute(query, args)
	return cursor, connection

def insert(query, args=()):
	cursor, connection = executeQuery(query, args)
	connection.commit()
	return cursor.lastrowid

def update(query, args=()):
	cursor, connection = executeQuery(query, args)
	connection.commit()
	return cursor.lastrowid

def selectOne(query, args=(), entity=None):
	cursor, connection = executeQuery(query, args)
	result = cursor.fetchone()
	if entity != None and result != None:
		return entity(*result)
	return result

def selectAll(query, args=(), entity=None):
	cursor, connection = executeQuery(query, args)
	result = cursor.fetchall()
	if entity != None and result != None:
		return [entity(*r) for r in result]
	return result


def initializeDatabase():
	script = open('sql/create.sql', 'r').read()
	executeScript(script)

def createTeam(teamName):
	return insert('INSERT INTO teams (name) VALUES (?)', (teamName,))

def findTeamById(teamId):
	return selectOne('SELECT * FROM teams WHERE id=?', (teamId,), Team)

def createUser(username, password, skype, teamId):
	return insert('INSERT INTO users (username, password, skype, team) VALUES (?, ?, ?, ?)', (username, password, skype, teamId))

def findUserById(userId):
	return selectOne('SELECT * FROM users WHERE id=?', (userId,), User)

def findUserBySkypeId(skypeId):
	return selectOne('SELECT * FROM users WHERE skype=?', (skypeId,), User)

def setUserMood(user, mood):
	entry = selectOne("SELECT * FROM entries WHERE userid=? AND entry_date=?", (user.id, today()), Entry)
	if entry == None:
		return insert("INSERT INTO entries (userid, mood, entry_date) VALUES (?, ?, ?)", (user.id, mood['score'], today()))
	else:
		return update("UPDATE entries SET mood=? WHERE id=?", (mood['score'], entry.id))


if __name__ == "__main__":
	initializeDatabase()
