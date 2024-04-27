bind = "0.0.0.0:8001"

workers = 2
threads = 4
worker_class = "uvicorn.workers.UvicornWorker"

loglevel = "debug"
accesslog = "-"
errorlog = "-"
