#!/bin/sh
# MQ preflight user-data: start the prepared Java HTTP server in the background.
set -eu
mkdir -p /var/log/mq
echo "user-data start $(date -u +%Y-%m-%dT%H:%M:%SZ) pid=$$ instance=${AWS_EC2_INSTANCE_ID:-unknown}" > /var/log/mq/user-data.marker
nohup java /opt/mq/HelloServer.java 8080 > /var/log/mq/server.log 2>&1 < /dev/null &
echo $! > /var/log/mq/server.pid
echo "user-data started java pid $(cat /var/log/mq/server.pid)"
