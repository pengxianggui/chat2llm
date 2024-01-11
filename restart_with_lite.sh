#!/bin/bash

chmod a+x shutdown_all.sh
./shutdown_all.sh
nohup python3 startup.py -a --lite > logs/restart_with_lite.output.log 2>&1 &
echo "Python3已在后台运行, 进程ID为 $!"




