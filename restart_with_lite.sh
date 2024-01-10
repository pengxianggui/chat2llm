#!/bin/bash

PID=$(ps -ef | grep "python3 startup.py -a --lite" | grep -v grep | awk '{print $2}')

if [ -n "$PID" ]; then
	echo "发现此脚本在运行中, 即将kill.."
	kill $PID
else
	echo "未发现此脚本在运行中, 即将直接启动.."
fi

nohup python3 startup.py -a --lite --config config.ini > logs/restart_with_lite.output.log 2>&1 &
echo "Python3已在后台运行, 进程ID为 $!"




