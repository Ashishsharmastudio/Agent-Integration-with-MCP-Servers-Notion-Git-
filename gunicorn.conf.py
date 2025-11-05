# gunicorn.conf.py
workers = 2
threads = 2
timeout = 120
graceful_timeout = 30
accesslog = "-"
errorlog = "-"
loglevel = "info"
