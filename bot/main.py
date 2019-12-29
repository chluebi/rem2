import discord
from lib.common import parse_config
from lib import database
from bot.util import parse_message
from bot.commands import execute_command

client = discord.Client()
config = parse_config('discord')
db_connection = database.connect()


@client.event
async def on_ready():
    print('------------------')
    print(f'bot ready {client.user.name}')
    print('------------------')


@client.event
async def on_message(message):
    p_message = parse_message(message.content)
    if p_message is not None:
        await execute_command(message, p_message, db_connection)

client.run(config['token'])