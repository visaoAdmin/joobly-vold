from background_api import sendHangout,endServiceCall,startServiceCall,sendRatings
from redis_queue import backgroundQueue

def failure_handler(job, connection, type, value, traceback):
    # print(type)
    args = job.__dict__['_args']
    function_ = job.__dict__['_func_name']
    print(function_)
    if("sendHangout" in function_):
        table,guestCount,waiterId,hangoutId = args 

        backgroundQueue.enqueue(sendHangout,table,guestCount,waiterId,hangoutId,at_front=True,on_failure=failure_handler)
    elif("endServiceCall" in function_):
        table ,hangoutId,callNumber,responseTime=args
        backgroundQueue.enqueue(endServiceCall,table ,hangoutId,callNumber,responseTime,at_front=True,on_failure=failure_handler)
        
    elif("startServiceCall" in function_):
        table,hangoutId,callNumber=args
        backgroundQueue.enqueue(startServiceCall,table,hangoutId,callNumber,at_front=True,on_failure=failure_handler)

    elif("sendRatings" in function_):
        table ,hangoutId,ratings=args
        backgroundQueue.enqueue(sendRatings,table ,hangoutId,ratings,at_front=True,on_failure=failure_handler)

    