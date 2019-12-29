
import time
import datetime
import calendar
import pytz


NUMS = ['0','1','2','3','4','5','6','7','8','9','.']


def timedelta_string_into_seconds(timestring):
    time_values = {'s':1,
                   'sec':1,
                   'm':60,
                   'min':60,
                   'h':3600,
                   'd':3600*24,
                   'w':3600*24*7,
                   'mon':3600*24*31,
                   'y':3600*24*365}
    end = []
    num = False
    abc = False
    timestring = timestring.replace(' ','')
    for let in timestring:
        if abc and num:
            raise Exception('This shouldn\'t happen')
        elif num:
            if let not in NUMS:
                end[-1][0] += let
            else:
                end[-1][1] += let
        elif abc:
            if let not in NUMS:
                end[-1][0] += let
            else:
                end.append(['', let])
        else:
            if let not in NUMS:
                num = False
                abc = not num
                continue

            end.append(['',let])

        abc = let not in NUMS
        num = not abc

    endsum = 0
    for form, amount in end:
        try:
            endsum += time_values[form] * float(amount)
        except:
            raise Exception(f'{form} is not a valid timetype')


    return endsum

def timepoint_string_to_seconds(timestring, timezone):
    target_time = strptime_list(timestring, timezone)
    if target_time is None:
        raise Exception('Not a valid format')
    return calendar.timegm(target_time)


def seconds_to_string(seconds):
    time_values = {'year': 3600 * 24 * 365,
                   'month': 3600 * 24 * 31,
                   'week': 3600 * 24 * 7,
                   'day': 3600 * 24,
                   'hour': 3600,
                   'minute': 60,
                   'second': 1
                   }

    rest = seconds
    end = []
    for key, value in time_values.items():
        if rest >= value:
            amount = int(rest // value)
            rest = rest % value
            if amount == 1:
                end.append(f'{amount} {key}')
            else:
                end.append(f'{amount} {key}s')

    if len(end) > 1:
        endstring = ', '.join(end[:-1])
        endstring += f' and {end[-1]}'
    elif len(end) > 0:
        endstring = end[0]
    else:
        endstring = '0 seconds'

    return endstring


def strptime_list(timestring, timezone):
    try:
        return time.strptime(timestring, '%Y')
    except:
        pass
    try:
        return time.strptime(timestring, '%Y.%m.%d')
    except:
        pass
    try:
        return time.strptime(timestring, '%d.%m.%Y')
    except:
        pass
    try:
        return time.strptime(timestring, '%Y.%m.%d %H:%M')
    except:
        pass
    try:
        return time.strptime(timestring, '%d.%m.%Y %H:%M')
    except:
        pass
    try:
        c = time.gmtime(delocalize_seconds(time.time(), timezone))
        end = time.strptime(f'{c.tm_year}.{c.tm_mon}.{c.tm_mday} {timestring}', '%Y.%m.%d %H:%M')
        if calendar.timegm(end) < delocalize_seconds(time.time(), timezone):
            end = time.gmtime(calendar.timegm(end) + 3600*24)
        return end
    except:
        pass
    try:
        c = time.gmtime(delocalize_seconds(time.time(), timezone))
        end = time.strptime(f'{c.tm_year}.{c.tm_mon}.{c.tm_mday} {timestring}', '%Y.%m.%d %H:%M:%S')
        if calendar.timegm(end) < delocalize_seconds(time.time(), timezone):
            end = time.gmtime(calendar.timegm(end) + 3600*24)
        return end
    except:
        pass


def datetime_to_timestring(datetime_object):
    return datetime_object.ctime()


def datetime_to_seconds(datetime_object):
    return (datetime_object-datetime.datetime(1970,1,1)).total_seconds()


def seconds_to_datetime(seconds):
    local = datetime.datetime.fromtimestamp(seconds)
    gmt = datetime.datetime.utcfromtimestamp(seconds)
    return local


def time_to_seconds(time_struct):
    return time.mktime(time_struct)


def seconds_to_time(seconds):
    return time.gmtime(seconds)


def localize_datetime(datetime_object, timezone):
    timezone = pytz.timezone(timezone)
    return datetime_object.astimezone(timezone)


def delocalize_seconds(seconds, timezone):
    timezone = pytz.timezone(timezone)
    datetime_object = seconds_to_datetime(seconds)
    offset = timezone.utcoffset(datetime_object).total_seconds()
    return seconds + offset


def localize_seconds(seconds, timezone):
    timezone = pytz.timezone(timezone)
    datetime_object = seconds_to_datetime(seconds)
    offset = timezone.utcoffset(datetime_object).total_seconds()
    return seconds - offset


if __name__ == '__main__':
    distance = timedelta_string_into_seconds('2s')
    point = time.time() + distance
    datetime_object = seconds_to_datetime(point)
    print(pytz.timezone('Europe/London').utcoffset(datetime_object))
    datetime_object = localize_datetime(datetime_object, 'Europe/London')
    datetime_string = datetime_to_timestring(datetime_object)
    print(datetime_object)