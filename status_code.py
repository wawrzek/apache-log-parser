#!/usr/bin/env python3

from datetime import datetime, date
import os.path
import re
import subprocess
import sys
from time import mktime


def _range(r1,r2):
    """
    This function returns a list of all the number between r1 and r2 arguments.
    It is used to created a list of all HTTP response values ranges.
    """
    return list(range(r1,r2))


def _get_time_value(response_log, apache_log):
    """
    This functions return the starting timestamp (as int).
    It first tries to read it from the response_log file.
    If that files doesn't exist, or the values is not valid read it from the apache_log file.
    If that is not possible, set it to begining of today.
    """
    try:
        with open(response_log, 'r') as f:
            return int(f.readline().split(',')[0])
    except (ValueError, FileNotFoundError):
        try:
            with open(apache_log, 'r') as f:
                return int(mktime(datetime.strptime(f.readline().split()[3][1:], '%d/%b/%Y:%H:%M:%S').timetuple()))
        except Exception:
            return int(mktime(date.today().timetuple()))

#DEFAULT VALUES
apache_log_path = "/var/log/apache2/"
apache_log = apache_log_path + "access.log"

response_log_path = ''
response_log = response_log_path + "response.log"

periods = {
    "sec": {
        "step": 1,
        "end": 19,
        "format_start": "%d/%b/%Y:%H:%M:%S",
        "format": "%d/%b/%Y:%H:%M:%S",
    },
    "min": {
        "step": 60,
        "end": 19,
        "format_start": "%d/%b/%Y:%H:%M:00",
        "format": "%d/%b/%Y:%H:%M:.{2}",
    },
    "hour": {
        "step": 60 * 60,
        "end": 14,
        "format_start": "%d/%b/%Y:%H:00:00",
        "format": "%d/%b/%Y:%H:.{2}:.{2}",
    },
    "day": {
        "step": 60 * 60 * 24,
        "end": 11,
        "format_start": "%d/%b/%Y:00:00:00",
        "format": "%d/%b/%Y:.{2}:.{2}:.{2}",
    },
}

line_log = '(?P<ip>[.:0-9a-fA-F]+) - - \[%s.{0,6}\] "GET (?P<uri>.*?) HTTP/1.\d" (?P<status_code>\d+) \d+ "(?P<referral>.*?)" "(?P<agent>.*?)"'

responses = _range(200,206) + _range(300,307) + _range(400,417) + _range(500,505)
status = { r:0 for r in responses}

t_resolution = 'hour'

if t_resolution in periods:
    time_step = periods[t_resolution]["step"]
    time_end_str =  datetime.strftime(datetime.now(), periods[t_resolution]["format_start"] )
    time_end = mktime(datetime.strptime(time_end_str, periods["sec"]["format_start"]).timetuple())
    str_end = periods[t_resolution]["end"]
else:
    print ("Wrong time resolution")
    sys.exit(4)

values=[]

print ("{},{}".format("date".rjust(str_end-4), ",".join([str(r) for r in responses])))

time_value = _get_time_value(response_log, apache_log)

while time_value <= time_end:
    values.append(str(time_value))
    if t_resolution in periods:
        time_string = datetime.strftime(datetime.fromtimestamp(time_value), periods[t_resolution]["format"])
    else:
        print ("Wrong time resolution")
        sys.exit(4)

    log_re = line_log%(time_string).format(time_string)
    search = re.compile(log_re).search

    matches = (search(line) for line in file(apache_log))

    for line in matches:
        if line:
            code = int((line.group('status_code')))
            status[code]= status[code]+1

    time_value = time_value + time_step
    print (time_string[:str_end] + ',' + ','.join(['%3d'%(status[r]) for r in responses]))
