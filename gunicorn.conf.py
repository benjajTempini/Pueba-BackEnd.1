# Gunicorn configuration file
import multiprocessing
import os

# Bind
bind = f"0.0.0.0:{os.getenv('PORT', '10000')}"

# Workers
workers = 2
worker_class = 'sync'

# Timeout
timeout = 120
graceful_timeout = 30
keepalive = 5

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Process naming
proc_name = 'ventasbasico'
