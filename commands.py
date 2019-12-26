import database as db
from util import parse_config
import timehandling as th
import time
import pytz

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

    await message.add_reaction('✅')
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
        m2 = 'Run ``{} timezone x`` to set it to a different value. \n'.format(config['prefix'])
        m3 = 'Here is a list of all available timezones: {} \n'.format(config['timezone_list'])
        m4 = '''(Where x is either your tz timezone (like ``Europe/London``)
or your UTC offset (like ``+3``/``-3``)'''
        await message.channel.send(m1 + m2 + m3 + m4)
        return

    timezone = msg[1]
    if timezone == user[1]:
        m1 = f'Your timezone is already ``{timezone}``. \n'
        await message.channel.send(m1)
        return

    if timezone[0] in ['+', '-', '0']:
        gmt = 'Etc/GMT'
        if int(timezone) <= 12 and int(timezone) >= -14:
            if int(timezone) >= 0:
                timezone = gmt + '+' + str(-int(timezone))
            else:
                timezone = gmt + '-' + str(-int(timezone))
            db.change_timezone(message.author.id, timezone)
            m1 = f'Your timezone has been set to ``{timezone}``. \n'
            await message.channel.send(m1)
            return

    if timezone in pytz.all_timezones:
        db.change_timezone(message.author.id, timezone)
        m1 = f'Your timezone has been set to ``{timezone}``. \n'
        await message.channel.send(m1)
        return
    
    m1 = f'The timezone ``{msg[1]}`` can\'t be found. \n'
    m2 = 'Here is a list of all available timezones: {} \n'.format(config['timezone_list'])
    await message.channel.send(m1 + m2)
    return


async def when(message, msg):
    user = db.get_user(message.author.id)

    if len(msg) < 2:
        await message.channel.send('Please specify a time')
        return

    try:
        distance = th.timedelta_into_seconds(msg[1])
        seconds_since_epoch = time.time() + distance
    except:
        try:
            seconds_since_epoch = th.timestring_to_seconds(msg[1], user[1])
            seconds_since_epoch = th.localize_seconds(seconds_since_epoch, user[1])
            distance = seconds_since_epoch - time.time()
        except Exception as e:
            await message.channel.send('''Error occured: ```{}``` 
                Be sure to use this format: ``{} when``'''.format(e, config['prefix']))
            return

    seconds_since_epoch += 3600
    datetime_object = th.seconds_to_datetime(seconds_since_epoch)
    datetime_object = th.localize_datetime(datetime_object, user[1])
    timedelta_string = th.seconds_to_string(distance)
    datetime_string = th.datetime_to_timestring(datetime_object)
    m = '''This timestamp is in ``{0}`` which is the ``{1}``'''\
    .format(timedelta_string, datetime_string)

    await message.channel.send(m)



#register_command(set_personal_reminder, name='personal', aliases=['me'])
register_command(set_timezone, name='timezone', aliases=['tz'])
register_command(when, name='when', aliases=[])