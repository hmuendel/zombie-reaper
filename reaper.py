#!/usr/bin/env python3
import logging
from collections import Counter
from time import sleep

import requests
import signal

from log_utils import configure

configure()
log = logging.getLogger('reaper')
log.debug(f'configuring ')

shutdown = False

def prepare_shutdown(s, ptr):
    global shutdown
    log.info(f'received termination signal: {s}, preparing shutdown')
    shutdown = True


signal.signal(signal.SIGINT, prepare_shutdown)
signal.signal(signal.SIGTERM, prepare_shutdown)



flagged_containers = {}
MAX_LEVEL = 3

log.info(f'searching garage for useful tools...')
# give the worker some time to come up
sleep(60)
log.info(f'🔥 now its time, fueling chainsaw...')
log.info('')
dead_zombies_total = 0
while not shutdown:
    try:
        dead_zombies = 0
        containers = requests.get('http://localhost:7777/containers').json()['Handles']
        log.info(f' 🔭 looking for zombies and found {len(containers)} containers')
        for container in containers:
            status = requests.get(f'http://localhost:7777/containers/{container}/info', timeout=1).status_code
            if status == 500:
                if container not in flagged_containers:
                    # log.info(f' First warning for container {container}')
                    flagged_containers[container] = 0
                else:
                    flagged_containers[container] += 1
                    if flagged_containers[container] > MAX_LEVEL:
                        # give garden 10 sec to kill the zombie
                        # log.info(f'🧟‍️ 🔫 Die zombie, {container} die!')
                        requests.put(f'http://localhost:7777/containers/{container}/grace_time', timeout=1, data=f'{10_000_000_000}')
                        del flagged_containers[container]
                        dead_zombies += 1
            else:
                if container in flagged_containers:
                    log.info(f'{container} seems innocent status became {status}')
                # else:
                #     log.info(f'{container} seems innocent from the beginning with {status}')
            # relax a little to not stress garden to much
            sleep(0.2)
        dead_zombies_total += dead_zombies
        log.info(f'killed {dead_zombies} 🧟‍ this round and {dead_zombies_total} in total️')
        log.info(f'{len(flagged_containers)} containers are behaving suspicious')
    except Exception:
        log.exception(f' failed reaping this time, waiting for next round')

    log.info('')
    log.info(f'Flagged containers (max_level: {MAX_LEVEL})')
    for k, v in Counter(flagged_containers.values()).items():
        log.info(f'Level {k}: {v} Containers')

    sleep(60)
log.info(f'done with reaping')
