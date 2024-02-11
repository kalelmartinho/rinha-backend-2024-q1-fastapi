import os

bind = os.getenv("BIND")
workers = os.getenv("WORKERS", 1)
backlog = os.getenv("BACKLOG", 64)
timeout = os.getenv("TIMEOUT", 60)
keepalive = 5
graceful_timeout = os.getenv("GRACEFUL_TIMEOUT", 30)
max_requests = os.getenv("MAX_REQUESTS", 0)
worker_class = os.getenv("WORKER_CLASS", "uvicorn.workers.UvicornWorker")
worker_tmp_dir = os.getenv("WORKER_TMP_DIR", "/dev/shm")

if os.getenv("KEEPALIVE"):
    keepalive = 120
    max_request_jitter = 0
