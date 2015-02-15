dashboard: mrq-dashboard
worker: mrq-worker highpriority default --scheduler
# http://docs.gunicorn.org/en/19.2.1/settings.html
web: gunicorn -w 4 -k gevent flaskapp.app:app
webnworker: sh -c "mrq-worker highpriority default --scheduler &; gunicorn -w 4 -k gevent flaskapp.app:app"