import time

from fastapi import Request


async def log_requests(request: Request, call_next):
    """
    Middleware de logging que registra cada request HTTP entrante.
    Mide la duración de cada petición y la imprime en consola con formato:
    MÉTODO /ruta → código_estado (duración_ms)
    """
    start = time.time()
    response = await call_next(request)
    duration = round((time.time() - start) * 1000, 2)
    print(f"{request.method} {request.url.path} → {response.status_code} ({duration}ms)")
    return response
    
