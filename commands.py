import database as db
from util import parse_config

config = parse_config()

commands = []

async def execute_command(message, msg):
	command = None
	for c in commands:
		if c.name == msg[0] or msg[0] in c.aliases:
			command = c
			break

	if command is None:
		await message.channel.send(f'Command ``{msg[0]}`` not found.')
		return

	await command.function(message, msg)


def register_command(function, name=None, aliases=[]):
	Command(function, name, aliases)


class Command:
	def __init__(self, function, name, aliases):
		self.function = function
		self.name = name
		self.aliases = aliases
		commands.append(self)


async def set_personal_reminder(message, msg):
	user = db.get_user(message.author.id)
	if user is None:
		m = 'Your timezone isn\'t set yet. Run ``{} timezone`` to set it.'.format(config['prefix'])
		db.create_user(message.author.id, 'Etc/GMT0')
		await message.channel.send(m)

async def set_timezone(message, msg):
	user = db.get_user(message.author.id)
	if user is None:
		db.create_user(message.author.id, 'Etc/GMT0')

	if len(msg) < 2:
		m1 = f'Your current timezone is ``{user[1]}``. \n'
		m2 = 'Run ``{} timezone x`` to set it. \n'.format(config['prefix'])
		m3 = '''(Where x is either your tz timezone (like ``Europe/London``)
or your UTC offset (like ``+3``/``-3``)'''
		await message.channel.send(m1 + m2 + m3)


#register_command(set_personal_reminder, name='personal', aliases=['me'])
register_command(set_timezone, name='timezone', aliases=['tz'])