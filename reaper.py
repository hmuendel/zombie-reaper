#!/usr/bin/env python

import requests
from time import sleep
from datetime import datetime

flagged_containers = {}

print(f'{datetime.now()}  searching garage for useful tools')
# give the worker some time to come up
sleep(60)
print(f'{datetime.now()} 🔥 now its time, fueling chainsaw...')
while True:
    containers = requests.get('http://localhost:7777/containers').json()['Handles']
    print(f'{datetime.now()}  🔭 looking for zombies')
    for container in containers:
        status = requests.get(f'http://localhost:7777/containers/{container}/info').status_code
        if status == 500:
            if not container in flagged_containers:
                print(f'{datetime.now()}  First warning for container {container}')
                flagged_containers[container] = 0
            else:
                flagged_containers[container] += 1
                if flagged_containers[container] > 10:
                    # give garden 1 sec to kill the zombie
                    print(f'{datetime.now()} 🧟‍️ 🔫 Die zombie, {container} die!')
                    requests.put(f'http://localhost:7777/containers/{container}/grace_time',
                             data=f'{1_000_000_000}').status_code
        # relax a little to not stress garden to much
        sleep(1)
    sleep(60)
