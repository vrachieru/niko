import sqlite3

class Sqlite(AbstractDatabase):
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