#!/usr/bin/env python

import os.path
import subprocess 
from datetime import datetime, timedelta
import time
import re


#VARIABLES
log_path = "/var/log/apache2/"
apache_log = log_path + "access.log"

t_resolution = 'day'

selected_type = 'responses'

values = {
'responses' : range(200,206) + range(300,307) + range(400,417) + range(500,505),
'requests'  : ['GET', 'POST', 'OPTIONS', 'PATCH', 'PUT', 'HEAD', 'CONNECT', 'DELETE', 'TRACE'],
}


if t_resolution == 'sec':
    time_step = timedelta(seconds=1)
    time_str = '%d/%b/%Y:%H:%M:%S'
elif t_resolution == 'min':
    time_step = timedelta(minutes=1)
    time_str = '%d/%b/%Y:%H:%M:00'
elif t_resolution == 'hour':
    time_step = timedelta(hours=1)
    time_str = '%d/%b/%Y:%H:00:00'
elif t_resolution == 'day':
    time_step = timedelta(days=1)
    time_str = '%d/%b/%Y:00:00:00'
else :
    print "Wrong step"
    sys.exit(4)

time = datetime.now() - time_step
   
if t_resolution == 'sec':
    time_string = datetime.strftime(time, '%d/%b/%Y:%H:%M:%S')
elif t_resolution == 'min':
    time_string = datetime.strftime(time, '%d/%b/%Y:%H:%M:.{2}')
elif t_resolution == 'hour':
    time_string = datetime.strftime(time, '%d/%b/%Y:%H:.{2}:.{2}')
elif t_resolution == 'day':
    time_string = datetime.strftime(time, '%d/%b/%Y:.{2}:.{2}:.{2}')

log_re = '(?P<ip>[.:0-9a-fA-F]+) - - \[%s.{0,6}\] "(?P<request>.*?) (?P<uri>.*?) HTTP/1.\d" (?P<status_code>\d+) \d+ "(?P<referral>.*?)" "(?P<agent>.*?)"'%(time_string)

search = re.compile(log_re).search

matches = (search(line) for line in file(apache_log))

selected = values[selected_type]
try:
    status = { r:0 for r in selected}

except KeyError:
    print "Please specify values of %s you would like to graph (e.g. set of IPs)"%selected

for line in matches :
    if line: 
        code = int((line.group('status_code')))
        status[code]= status[code]+1

#print str('%-11s'%'date') + ',' + ','.join([str(r) for r in values[selected_type]))
print time_string[:11] + ',' + ','.join(['%3d'%(status[r]) for r in selected])

