#!/bin/bash
python3 make_env.py
cd BitmoonExchanger
celery -A BitmoonExchanger worker -l info --concurrency=4 --prefetch-multiplier=1
