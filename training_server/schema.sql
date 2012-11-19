drop table if exists events;
create table events (
	id integer primary key autoincrement,
	start datetime,
	team1 integer references teams(id),
	team2 integer references teams(id),
	location text,
	score text,
	UNIQUE (team1, team2, start)
);

drop table if exists teams;
create table teams (
	id integer primary key autoincrement,
	loc text,
	name text
);

drop table if exists documents;
create table documents (
	id integer primary key autoincrement,
	url text,
	content text,
	time_created datetime default CURRENT_TIMESTAMP,
	UNIQUE (url, content)
);

drop table if exists votes;
create table votes (
	id integer primary key autoincrement,
	vote boolean positive default "False", --positive means it should be blocked
	document integer references documents(id) not null,
	event integer references events(id) not null,
	time datetime default CURRENT_TIMESTAMP,
	ip_addr text
);