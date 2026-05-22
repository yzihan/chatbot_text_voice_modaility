import os
from dotenv import load_dotenv

# set env file for wsgi 
load_dotenv(dotenv_path=".env")
bind = "0.0.0.0:8000"
# workers = 0
worker_class = "uvicorn.workers.UvicornWorker"
daemon = True
timeout = 120
