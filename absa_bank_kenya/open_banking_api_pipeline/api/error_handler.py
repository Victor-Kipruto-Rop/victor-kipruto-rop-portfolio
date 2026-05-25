from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

async def api_error_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        return JSONResponse(status_code=exc.status_code, content={"status": "error", "message": exc.detail})
    return JSONResponse(status_code=500, content={"status": "error", "message": "An unexpected error occurred."})
