#!/bin/sh
mrq-worker highpriority default 3d --scheduler --greenlets 30 &

# http://docs.gunicorn.org/en/19.2.1/settings.html
gunicorn --worker-connections 50 -w 3 -k gevent flaskapp.app:app --log-file -