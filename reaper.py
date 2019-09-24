#!/usr/bin/env python3
import logging
from collections import Counter
from time import sleep

import requests
import signal
import shutil
import os
from prometheus_client import start_http_server, Gauge, Counter
from log_utils import configure

label_names = []
label_values = []
TOTAL_SPACE = Gauge('concourse_reaper_volumes_space_total_bytes',
                    'the total available storage in bytes of the concourse work dir btrfs subvolume', label_names, label_values)
FREE_SPACE = Gauge('concourse_reaper_volumes_space_free_bytes',
                   'the free storage in bytes of the concourse work dir btrfs subvolume', label_names, label_values)
USED_SPACE = Gauge('concourse_reaper_volumes_space_used_bytes',
                   'the used storage in bytes of the concourse work dir btrfs subvolume', label_names, label_values)
ZOMBIES = Counter('concourse_reaper_killed_zombies_count', 'total number of slain zombie containers', label_names, label_values)

configure()
log = logging.getLogger('reaper')
log.debug(f'configuring ')

shutdown = False


def emit_metrics(zombies):
    try:
        total, used, free = shutil.disk_usage('/concourse-workdir/volumes')
        TOTAL_SPACE.set(total)
        USED_SPACE.set(used)
        FREE_SPACE.set(free)
        # ZOMBIES.inc(zombies)

    except Exception as e:
        print(e)


def prepare_shutdown(s, ptr):
    global shutdown
    log.info(f'received termination signal: {s}, preparing shutdown')
    shutdown = True


signal.signal(signal.SIGINT, prepare_shutdown)
signal.signal(signal.SIGTERM, prepare_shutdown)

flagged_containers = {}
MAX_LEVEL = 3

log.info(f'searching garage for useful tools...')
start_http_server(8000)
# give the worker some time to come up
sleep(60)
log.info(f'🔥 now its time, fueling chainsaw...')
log.info('')
dead_zombies_total = 0
while not shutdown:
    try:
        emit_metrics(dead_zombies_total)
        dead_zombies = 0
        containers = requests.get('http://localhost:7777/containers').json()['Handles']
        log.info(f' 🔭 looking for zombies and found {len(containers)} containers')
        for container in containers:
            if shutdown:
                break
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
                        requests.put(f'http://localhost:7777/containers/{container}/grace_time', timeout=1,
                                     data=f'{10_000_000_000}')
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
