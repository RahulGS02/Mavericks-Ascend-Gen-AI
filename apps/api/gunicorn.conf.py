# Gunicorn configuration file for Azure deployment
import multiprocessing
import os

# Bind to the port provided by Azure
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"

# Worker processes
workers = 1  # Use 1 worker for Free tier
worker_class = "uvicorn.workers.UvicornWorker"

# Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"

# Timeout
timeout = 120
keepalive = 5

# Application
wsgi_app = "app.main:app"
