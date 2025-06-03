import multiprocessing

max_requests = 1000
max_requests_jitter = 50
log_file = "-"
bind = "0.0.0.0:9000"
workers = 1#(multiprocessing.cpu_count() * 2) + 1

worker_class = "src.my_uvicorn_worker.MyUvicornWorker"

timeout = 600