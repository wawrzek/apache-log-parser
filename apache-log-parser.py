#!/usr/bin/env python

import os.path
import sys 
from datetime import datetime, timedelta
import time
import re
from optparse import OptionParser


#VARIABLES
log_path = "/var/log/apache2/"
apache_log = log_path + "access.log"

#DEFAULT VALUES
t_resolution = 'day'
selected_type = 'responses'


values = {
'responses' : {"type" : "int", "name": "status_code", "elements": range(200,206) + range(300,307) + range(400,417) + range(500,505)},
'requests'  : {"type" : "str", "name": "request", "elements": ['GET', 'POST', 'OPTIONS', 'PATCH', 'PUT', 'HEAD', 'CONNECT', 'DELETE', 'TRACE']},
}

parser = OptionParser()
parser.add_option("-r", "--resolution", dest="resolution", action="store", type="string",
                help="define time resolution (e.g. 1 sec = sec) can be sec, min, hour, day")
parser.add_option("-m", "--measure", dest="measure", action="store", type="string",
                help="""define what to measurement (predefine HTTP responses and requests)
but it also cand be easily define for uri, ip address, referral or agent string.
    Prefine responses (status codes) are in range: 200, 201, 202, 203, 204, 205, 206, 300, 301, 302, 303, 304, 305, 306, 307, 400, 401, 402, 403, 404, 405, 406, 407, 408, 409, 410, 411, 500, 501, 502, 503, 504, 505 \n\
    Prefine request are: GET, POST, OPTIONS, PATCH, PUT, HEAD, CONNECT, DELETE, TRACE """)

(options, args) = parser.parse_args()

if options.measure:
    selected_type = options.measure
if options.resolution:
    t_resolution = options.resolution

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
    time_output = '%H:%M:%s'
    time_string = datetime.strftime(time, '%d/%b/%Y:%H:%M:%S')
    time_output = datetime.strftime(time, '%H:%M:%S')
elif t_resolution == 'min':
    time_string = datetime.strftime(time, '%d/%b/%Y:%H:%M:.{2}')
    time_output = datetime.strftime(time, '%H:%M')
elif t_resolution == 'hour':
    time_string = datetime.strftime(time, '%d/%b/%Y:%H:.{2}:.{2}')
    time_output = datetime.strftime(time, '%H')
elif t_resolution == 'day':
    time_string = datetime.strftime(time, '%d/%b/%Y:.{2}:.{2}:.{2}')
    time_output = datetime.strftime(time, '%d/%b/%Y')

log_re = '(?P<ip>[.:0-9a-fA-F]+) - - \[%s.{0,6}\] "(?P<request>.*?) (?P<uri>.*?) HTTP/1.\d" (?P<status_code>\d+) \d+ "(?P<referral>.*?)" "(?P<agent>.*?)"'%(time_string)

search = re.compile(log_re).search

matches = (search(line) for line in file(apache_log))

selected = values[selected_type]
try:
    status = { r:0 for r in selected["elements"]}
except KeyError:
    print "Please specify values of %s you would like to graph (e.g. set of IPs)"%selected

for line in matches :
    if line:
        code = eval(selected["type"])(line.group(selected["name"]))
        status[code]= status[code]+1
#print str('%-11s'%'date') + ',' + ','.join([str(r) for r in values[selected_type]))
print time_output + ',' + ','.join(['%3d'%(status[r]) for r in selected["elements"]])

