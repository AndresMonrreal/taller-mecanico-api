import time

from fastapi import Request

async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000,2) 
    print(f"{request.method} {request.url.path} → {response.status_code} ({duration}ms)")
    return response
    
