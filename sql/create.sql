CREATE TABLE IF NOT EXISTS users (
	id integer PRIMARY KEY,
	username string NOT NULL,
	password string NOT NULL,
	skype string NOT NULL,
	team integer NOT NULL
);

CREATE TABLE if not exists entries (
	id integer PRIMARY KEY,
	userid integer NOT NULL,
	mood integer NOT NULL,
 	entry_date date NOT NULL
);

CREATE TABLE if not exists teams (
	id integer PRIMARY KEY,
	name string NOT NULL
);