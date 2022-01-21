#!/bin/sh
export FLASK_APP=bankAPI
export FLASK_ENV=dev
export FLASK_DEBUG=True
# source $(pipenv --venv)/bin/activate
python bankAPI/model/database.py
python bankAPI/load_data.py
flask run -h 0.0.0.0