import os
import sys
import time
from datetime import datetime
from string import Template

import requests

DELAY_SECONDS = 30
SNORE_MINUTES_WAIT = 2

modes = ['change', 'increase', 'decrease']
if (len(sys.argv) == 1 or len(sys.argv) > 3) or \
        (not sys.argv[1].isdigit()) or \
        (len(sys.argv) == 3 and not sys.argv[2] in modes):
    print 'SYNTAX:\n\tpython ' + sys.argv[0] + ' nation_id [(change)|increase|decrease]'
    exit(1)

nation_id = sys.argv[1]
nation_url = 'https://politicsandwar.com/api/nation/id=' + nation_id
message_template = Template('${nation_name}\'s score has changed from ${base_score} to ${new_score}')

response = requests.get(nation_url)
if not response.json()['success']:
    print 'Error fetching data for nation ' + sys.argv[1] + '.'
    print response.json()['error']
    exit(2)
base_score = new_score = response.json()['score']
nation_name = response.json()['name']
mode = 'change' if len(sys.argv) != 3 else sys.argv[2]

print 'Monitoring ' + nation_name + ' with nation id ' + nation_id + ' for nation score ' + mode + ' from ' + base_score
while True:
    if datetime.utcnow().hour % 2 == 0 and datetime.utcnow().minute < SNORE_MINUTES_WAIT:
        time.sleep(DELAY_SECONDS)
        continue
    response = requests.get(nation_url)
    new_score = response.json()['score']

    if new_score != base_score:
        print '[' + time.ctime() + '] ' + message_template.substitute(nation_name=nation_name,
                                                                      base_score=base_score,
                                                                      new_score=new_score)
        if mode == modes[0] or \
                (mode == modes[1] and new_score > base_score) or \
                new_score < base_score:
            os.system('say "Warning! ' + message_template.substitute(nation_name=nation_name,
                                                                     base_score=base_score,
                                                                     new_score=new_score) + '"')
            os.system('printf \'\a\'')
            exit(0)
        base_score = new_score
    time.sleep(DELAY_SECONDS)
