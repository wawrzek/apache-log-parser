#!/usr/bin/env python


import os.path
import subprocess 
from datetime import datetime, date
import time
import re


#VARIABLES
log_path = "/var/log/apache2/"
apache_log = log_path + "access.log"

log_path = ''
response_log = log_path + "response.log"

response_file = open(response_log,'a')

t_resolution = 'hour'

responses = range(200,206) + range(300,307) + range(400,417) + range(500,505)

# SET INITIAL TIME   
# FIRST TIME FROM PREVIOUS RUN
try:
    time_value = int((open(response_log,'r').readline().split(',')[0]))
except ValueError, IOError:
# NEXT TIME FROM LOG FILE
    try :
        time_value = int(time.mktime(datetime.strptime(open(apache_log,'r').readline().split()[3][1:],'%d/%b/%Y:%H:%M:%S').timetuple()))
# FINALLY BEGINING OF TODAY
    except Exception:
        time_value = int(time.mktime(date.today().timetuple()))

# SET TIME RESOLUTION - STRING FOR END SEARCH
if t_resolution == 'sec':
    time_step = 1
    time_end_str = datetime.strftime(datetime.now(), '%d/%b/%Y:%H:%M:%S')
    str_end = 19
elif t_resolution == 'min':
    time_step = 60
    time_end_str = datetime.strftime(datetime.now(), '%d/%b/%Y:%H:%M:00')
    str_end = 17
elif t_resolution == 'hour':
    time_step = 60 * 60
    time_end_str = datetime.strftime(datetime.now(), '%d/%b/%Y:%H:00:00')
    str_end = 14
elif t_resolution == 'day':
    time_step = 60 * 60 * 24
    time_end_str = datetime.strftime(datetime.now(), '%d/%b/%Y:00:00:00')
    str_end = 11
else :
    print "Wrong resolution"
    sys.exit(4)

time_end = time.mktime(datetime.strptime(time_end_str, '%d/%b/%Y:%H:%M:%S').timetuple())


values=[]

print "date" + ' '*(str_end-4) + ',' + ','.join([str(r) for r in responses])

while time_value <= time_end:
    values.append(str(time_value))
# SET STRING TO SEARCH
    if t_resolution == 'sec':
        time_string = datetime.strftime(datetime.fromtimestamp(time_value), '%d/%b/%Y:%H:%M:%S')
    elif t_resolution == 'min':
        time_string = datetime.strftime(datetime.fromtimestamp(time_value), '%d/%b/%Y:%H:%M:.{2}')
    elif t_resolution == 'hour':
        time_string = datetime.strftime(datetime.fromtimestamp(time_value), '%d/%b/%Y:%H:.{2}:.{2}')
    elif t_resolution == 'day':
        time_string = datetime.strftime(datetime.fromtimestamp(time_value), '%d/%b/%Y:.{2}:.{2}:.{2}')
    log_re = '(?P<ip>[.:0-9a-fA-F]+) - - \[%s.{0,6}\] "GET (?P<uri>.*?) HTTP/1.\d" (?P<status_code>\d+) \d+ "(?P<referral>.*?)" "(?P<agent>.*?)"'%(time_string)
    search = re.compile(log_re).search

    matches = (search(line) for line in file(apache_log))

    # Zero for each status code
    status = { r:0 for r in responses}
    # Count status codes
    for line in matches :
        if line: 
            code = int((line.group('status_code')))
            status[code]= status[code]+1

    time_value = time_value + time_step
    print time_string[:str_end] + ',' + ','.join(['%3d'%(status[r]) for r in responses])
#print (r_row)


