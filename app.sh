#!/bin/bash

# 初始化数据库
python seed_db.py

# 启动应用
gunicorn app:app --bind 0.0.0.0:7860 --workers 1 --threads 8 