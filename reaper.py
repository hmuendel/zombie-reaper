import requests
from time import sleep

while True:
    print(':fire: fueling chainsaw')
    containers = requests.get('http://localhost:7777/containers').json()['Handles']
    print(f':telescope: looking for zombies')
    for container in containers:
        status = requests.get(f'http://localhost:7777/containers/{container}/info').status_code
        if status == 500:
            # give garden 1 sec to kill the zombie
            print(':zombie: :gun: Die zombie, die!')
            requests.put(f'http://localhost:7777/containers/{container}/grace_time',
                         data=f'{1_000_000_000}').status_code
    sleep(30)
