import sqlite3

database = 'niko.db'
connection = sqlite3.connect(database)
cursor = connection.cursor()

def create_db():
	cursor.executescript('''
		create table if not exists users (
			id integer primary key,
			username string not null,
			password string not null,
			skype string not null,
			team integer
		);

		create table if not exists entries (
			id integer primary key,
			userid integer,
			mood integer,
		 	entry_date date
		);

		create table if not exists teams (
			id integer primary key,
			name string not null
		);''')
	
	connection.commit()


def create_team(team_name):
  cursor.execute('insert into teams (name) values (?)', (team_name,))
  connection.commit()
  return cursor.lastrowid

def create_user(username, password, skype, team):
  cursor.execute('insert into users (username, password, skype, team) values (?, ?, ?, ?)', (username, password, skype, team))
  connection.commit()

create_db()
teamId = create_team('team')
create_user('user', 'pass', 'skype', teamId)
connection.close()