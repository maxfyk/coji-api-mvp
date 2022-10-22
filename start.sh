#!/bin/bash
echo "Starting to trigger gunicorn"
#gunicorn api:app -w 1 --threads 2 -b 0.0.0.0:8000 &
python /app/api.py
echo "Starting Nginx Service"
nginx -g 'daemon off;'