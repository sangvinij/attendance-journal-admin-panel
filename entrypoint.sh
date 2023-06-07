#!/bin/bash
python project/manage.py migrate
python project/create_users_in_db_script.py
python project/manage.py runserver 0.0.0.0:8000
