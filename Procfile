worker: mrq-worker highpriority default 3d --scheduler --greenlets 30

web: gunicorn --worker-connections 50 -w 3 -k gevent flaskapp.app:app --log-file -
# web: sh webnworker.sh