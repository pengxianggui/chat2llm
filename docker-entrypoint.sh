#!/bin/bash

cd /app
echo "current dir: $(pwd)"

#site_packages="/app/.site-packages"
## 如果site_packages是空目录，则安装依赖
#if [ "$(ls -A $site_packages)" = "" ]; then
#  install_cmd="pip3 install -r ./requirements.txt -r ./requirements_api.txt -r ./requirements_lite.txt --target=${site_packages}"
#  echo "execute: $install_cmd"
#  eval "$install_cmd"
#fi

install_cmd="pip3 install -r ./requirements_lite.txt"
echo "execute: $install_cmd"
eval "$install_cmd"

# 如果knowledge_base为空，表示库未初始化, 则初始化
if [ "$(ls -A knowledge_base)" = "" ]; then
  init_db_cmd="python3 init_database.py --recreate-vs"
  echo "execute: $init_db_cmd"
  eval "$init_db_cmd"
fi

cmd="python3 startup.py -a --lite"
echo "execute: $cmd"
eval "$cmd"

exec "$@"