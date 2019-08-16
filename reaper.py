import requests
from time import sleep
from datetime import datetime

print(f'{datetime.now()}  fueling chainsaw')
# give the worker some time to come up
sleep(60)
print(f'{datetime.now()} 🔥 now its time, fueling chainsaw...')
while True:
    containers = requests.get('http://localhost:7777/containers').json()['Handles']
    print(f'{datetime.now()}  🔭 looking for zombies')
    for container in containers:
        status = requests.get(f'http://localhost:7777/containers/{container}/info').status_code
        if status == 500:
            # give garden 1 sec to kill the zombie
            print(f'{datetime.now()}  🧟🧟‍️ 🔫 Die zombie, die!')
            requests.put(f'http://localhost:7777/containers/{container}/grace_time',
                         data=f'{1_000_000_000}').status_code
            # relax a little to not stress garden to much
            sleep(1)
    sleep(60)
