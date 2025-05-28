#!/bin/bash


VENV_PATH="./venv/bin/activate"
# 定义 Gunicorn 配置文件的路径
CONFIG_FILE="gunicorn_conf.py"


echo "Activating virtual environment..."
source $VENV_PATH


# 查找并杀死所有运行的 Gunicorn 进程
echo "Terminating existing Gunicorn processes..."
pgrep -f $CONFIG_FILE | xargs kill -9

# 启动 Gunicorn
echo "Starting Gunicorn..."
gunicorn -c $CONFIG_FILE main:hub

echo "Gunicorn has been restarted."
