#!/bin/sh
mrq-worker highpriority default --scheduler &
gunicorn -w 4 -k gevent flaskapp.app:app