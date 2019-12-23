import psycopg2
from util import parse_db_config

def db_connect():
	config = parse_db_config()
	conn = psycopg2.connect(host=config['host'],
	 						port=config['port'],
	 						database=config['database'],
	  						user=config['user'],
	   						password=config['password'])

	return conn

def create_tables():
	commands = (
		'''
		CREATE TABLE users (
			user_id bigint PRIMARY KEY,
			user_timezone VARCHAR(255)
		);
		''',
		'''
		CREATE TABLE timers (
			timer_id SERIAL,
			timer_timestamp_created double precision,
			timer_timestamp_triggered double precision,
			timer_author_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
			timer_guild INTEGER,
			timer_channel INTEGER,
			PRIMARY KEY (timer_id, timer_author_id)
		);
		''')

	conn = db_connect()
	cur = conn.cursor()

	for c in commands:
		cur.execute(c)

	conn.commit()
	cur.close()
	conn.close()


def get_user(user_id):
	conn = db_connect()
	cur = conn.cursor()
	command = '''SELECT * FROM users WHERE user_id = %s'''
	cur.execute(command, (user_id,))
	row = cur.fetchone()
	cur.close()
	conn.close()
	return row


def create_user(user_id, user_timezone):
	conn = db_connect()
	cur = conn.cursor()
	command = '''INSERT INTO users(user_id, user_timezone) VALUES (%s, %s);'''
	cur.execute(command, (user_id, user_timezone))
	conn.commit()
	cur.close()
	conn.close()
