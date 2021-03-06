import lib.database as db
from lib.common import parse_config, get_message_link
from bot.util import is_dm
import lib.time_handle as th

import time
import pytz
from math import floor


config = parse_config('discord')

commands = []

async def execute_command(client, message, msg, db_connection):
    command = None
    for c in commands:
        if c.name == msg[0] or msg[0] in c.aliases:
            command = c
            break

    if command is None:
        await message.channel.send(f'Command ``{msg[0]}`` not found.')
        return

    await message.add_reaction('✅')
    await command.function(client, message, msg, db_connection)


def register_command(function, name=None, aliases=[]):
    Command(function, name, aliases)


class Command:
    def __init__(self, function, name, aliases):
        self.function = function
        self.name = name
        self.aliases = aliases
        commands.append(self)



async def set_timezone(client, message, msg, db_connection):
    user = db.get_user(db_connection, message.author.id)
    if user is None:
        db.create_user(db_connection, message.author.id, 'Etc/GMT0')

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
            db.change_timezone(db_connection, message.author.id, timezone)
            m1 = f'Your timezone has been set to ``{timezone}``. \n'
            await message.channel.send(m1)
            return

    if timezone in pytz.all_timezones:
        db.change_timezone(db_connection, message.author.id, timezone)
        m1 = f'Your timezone has been set to ``{timezone}``. \n'
        await message.channel.send(m1)
        return
    
    m1 = f'The timezone ``{msg[1]}`` can\'t be found. \n'
    m2 = 'Here is a list of all available timezones: {} \n'.format(config['timezone_list'])
    await message.channel.send(m1 + m2)
    return


async def when(client, message, msg, db_connection):
    user = db.get_user(db_connection, message.author.id)
    if user is None:
        db.create_user(db_connection, message.author.id, 'Etc/GMT0')
        user = db.get_user(db_connection, message.author.id)

    if len(msg) < 2:
        await message.channel.send('Please specify a time')
        return

    try:
        distance = th.timedelta_string_into_seconds(msg[1])
        seconds_since_epoch = time.time() + distance
    except:
        try:
            seconds_since_epoch = th.timepoint_string_to_seconds(msg[1], user[1])
            seconds_since_epoch = th.localize_seconds(seconds_since_epoch, user[1])
            distance = seconds_since_epoch - time.time()
        except Exception as e:
            await message.channel.send('''Error occured: ```{}``` 
                Be sure to use this format: ``{} when``'''.format(e, config['prefix']))
            return

    datetime_object = th.seconds_to_datetime(seconds_since_epoch)
    datetime_object = th.localize_datetime(datetime_object, user[1])
    timedelta_string = th.timedelta_seconds_to_string(distance)
    datetime_string = datetime_object.ctime()
    m = '''This timestamp is in ``{0}`` which is the ``{1}``'''\
    .format(timedelta_string, datetime_string)

    await message.channel.send(m)


async def timer_list(client, message, msg, db_connection):
    user = db.get_user(db_connection, message.author.id)
    if user is None:
        m = 'You don\'t have any timers set yet.'
        await message.channel.send(m)

    timers = db.get_timers(db_connection, message.author.id)
    # timers = id | label | timestamp_created | timestamp_triggered | author_id | receiver_id | guild | channel | message
    # rows = label | timestamp_created | timestamp_triggered | author_id | receiver_id | link
    row = '| {0} | {1} | {2} | {3} | {4} |\n'
    

    def make_length(string, l):
        if len(string) >= l:
            return string[:l]

        white = ''.join([' ' for _ in range(floor((l - len(string))/2))])
        extrawhitespace = ' ' if divmod(l - len(string), 2)[1] == 1 else ''
        return white + extrawhitespace + string + white

    row_data = []
    for t in timers:
        label = str(t[1])
        timestamp_created = time.ctime(t[2])
        timestamp_triggered = time.ctime(t[3])
        author = str(client.get_user(t[4]))
        receiver = str(client.get_user(t[5]))
        #link = make_length(get_message_link(t[6], t[7], t[8], t[4]), 70)
        row_data.append((label, timestamp_created, timestamp_triggered, author, receiver))

    max_lens = []
    max_lens.append(max([len(i[0]) for i in row_data]))
    max_lens.append(max([len(i[1]) for i in row_data]))
    max_lens.append(max([len(i[2]) for i in row_data]))
    max_lens.append(max([len(i[3]) for i in row_data]))
    max_lens.append(max([len(i[4]) for i in row_data]))

    s = sum(max_lens) + len(max_lens) * 3

    rows = []
    rows.append(''.join(['-' for _ in range(s)]) + '\n')

    for t in row_data:
        label = make_length(t[0], max_lens[0])
        timestamp_created = make_length(t[1], max_lens[1])
        timestamp_triggered = make_length(t[2], max_lens[2])
        author = make_length(t[3], max_lens[3])
        receiver = make_length(t[4], max_lens[4])
        r = row.format(label, timestamp_created, timestamp_triggered, author, receiver)
        rows.append(r)

    rows.append(''.join(['-' for _ in range(s)]) + '\n')

    m = '''```\n{}```'''.format(''.join(rows))

    await message.channel.send(m)


async def set_personal_reminder(client, message, msg, db_connection):
    user = db.get_user(db_connection, message.author.id)
    if user is None:
        m = 'Your timezone isn\'t set yet. Run ``{} timezone`` to set it.'.format(config['prefix'])
        db.create_user(db_connection, message.author.id, 'Etc/GMT0')
        await message.channel.send(m)
        return

    if len(msg) < 2:
        await message.channel.send('Please specify a time')
        return

    if len(msg) < 3:
        msg.append('timer')

    try:
        distance = th.timedelta_string_into_seconds(msg[1])
        seconds_since_epoch = time.time() + distance
    except:
        try:
            seconds_since_epoch = th.timepoint_string_to_seconds(msg[1], user[1])
            seconds_since_epoch = th.localize_seconds(seconds_since_epoch, user[1])
            distance = seconds_since_epoch - time.time()
        except Exception as e:
            await message.channel.send('''Error occured: ```{}``` 
                Be sure to use this format: ``{} when``'''.format(e, config['prefix']))
            return

    datetime_object = th.seconds_to_datetime(seconds_since_epoch)
    datetime_object = th.localize_datetime(datetime_object, user[1])
    timedelta_string = th.timedelta_seconds_to_string(distance)
    datetime_string = datetime_object.ctime()

    channel = message.channel

    if is_dm(channel):
        guild = 0
    else:
        guild = message.channel.guild.id

    channel = channel.id

    m = '''Timer **{0}** set for you **{1}** which is in **{2}**'''\
    .format(msg[2], datetime_string, timedelta_string)

    db.create_timer(db_connection, msg[2], time.time(), seconds_since_epoch, \
     message.author.id, receiver_id=message.author.id, guild_id=guild, \
     channel_id=channel, message_id=message.id)

    await message.channel.send(m)



#register_command(set_personal_reminder, name='personal', aliases=['me'])
register_command(set_timezone, name='timezone', aliases=['tz'])
register_command(when, name='when', aliases=[])
register_command(set_personal_reminder, name='me', aliases=['m', 'myself'])
register_command(timer_list, name='list', aliases=['l'])