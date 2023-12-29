#!/bin/bash

PID=$(ps -ef | grep "python3.10 startup.py -a --lite" | grep -v grep | awk '{print $2}')

if [ -n "$PID" ]; then
	echo "发现此脚本${PID}在运行中, kill.."
	kill $PID
else
	echo "未发现此脚本在运行中"
fi





