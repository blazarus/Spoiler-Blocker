drop table if exists events;
create table events (
	id integer primary key autoincrement,
	start datetime,
	team1_name text,
	team1_loc text,
	team2_name text,
	team2_loc text,
	location text,
	score text
);

drop table if exists documents;
create table documents (
	id integer primary key autoincrement,
	url text,
	content text,
	time_written datetime
);

drop table if exists votes;
create table votes (
	id integer primary key autoincrement,
	boolean positive default "false", --positive means it should be blocked
	document integer references documents(id) not null,
	event integer references events(id) not null,
	time datetime,
	ip_addr text
);