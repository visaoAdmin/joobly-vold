from rq import Queue
from redis import Redis
import background_api
import time
backgroundQueue = Queue('low',connection=Redis('localhost',6379))
foregroundQueue = Queue('high',connection=Redis('localhost',6379))

def handle_failure(job, connection, type, value, traceback):
    print("#################################################################################")
    function_name = job.__dict__['_func_name']
    args = job.__dict__['_args']
    
    # backgroundQueue.enqueue(exec(function_name = job.__dict__['_func_name']),*args,on_failure=handle_failure,)
     

