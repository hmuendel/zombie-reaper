#!/usr/bin/env bash

lo="$(losetup -j /concourse-work-dir/volumes.img | cut -d':' -f1)"
if [ -z "$lo" ]; then
  lo="$(losetup -f --show /concourse-work-dir/volumes.img)"
fi
mount -t btrfs $lo /mnt

python -u ./reaper.py
