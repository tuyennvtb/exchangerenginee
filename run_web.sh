#!/bin/bash
python3 make_env.py
cd BitmoonExchanger
python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:8000 &
celery -A BitmoonExchanger beat -l info
