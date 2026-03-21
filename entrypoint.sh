#!/bin/bash
env >> /etc/environment
exec cron -l 2 -f
