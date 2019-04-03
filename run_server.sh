#!/bin/sh

cd /code
flask db upgrade
flask db migrate
exec flask run -h 0.0.0.0
