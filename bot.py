import discord
from util import parse_config, parse_message
from commands import execute_command

client = discord.Client()
config = parse_config()

@client.event
async def on_ready():
	print('------------------')
	print(f'bot ready {client.user.name}')
	print('------------------')

@client.event
async def on_message(message):
	p_message = parse_message(message.content)
	if p_message is not None:
		await execute_command(message, p_message)

client.run(config['token'])