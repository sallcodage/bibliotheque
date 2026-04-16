#!/usr/bin/env bash
set -o errexit
gunicorn bibliotheque.wsgi:application --bind 0.0.0.0:$PORT --workers 2