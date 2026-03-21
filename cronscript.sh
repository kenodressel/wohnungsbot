#!/bin/bash
. /etc/environment
echo "Job started: $(date)"
/usr/local/bin/python -u /root/wohnungen.py
echo "Job finished: $(date)"
