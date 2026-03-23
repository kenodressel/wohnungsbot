#!/bin/bash
env >> /etc/environment

MARKER="/root/data/.migrated_to_link_ids"
if [ ! -f "$MARKER" ]; then
    echo "First run: seeding link-based IDs..."
    /usr/local/bin/python -u /root/wohnungen.py --seed
    if [ $? -eq 0 ]; then
        touch "$MARKER"
        echo "Seed complete."
    else
        echo "ERROR: Seed failed. Will retry on next restart."
    fi
fi

exec cron -l 2 -f
