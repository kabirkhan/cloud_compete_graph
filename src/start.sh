#!/bin/bash
uwsgi --http :${PORT} --wsgi-file app/server.py --callable __hug_wsgi__ --master --uid www-data --processes 2