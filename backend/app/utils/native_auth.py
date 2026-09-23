from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import base64
import os

class SwaggerAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        # Only protect Swagger endpoints
        if request.url.path in ["/docs", "/openapi.json"]:
            auth_header = request.headers.get("Authorization")
            
            if not auth_header:
                return Response(
                    "Unauthorized",
                    status_code=401,
                    headers={"WWW-Authenticate": "Basic realm='Swagger UI'"}
                )
            
            try:
                # Parse Basic Auth
                scheme, credentials = auth_header.split(" ")
                if scheme.lower() != "basic":
                    return Response("Unauthorized", status_code=401)
                
                decoded = base64.b64decode(credentials).decode("utf-8")
                username, password = decoded.split(":", 1)
                
                # Check credentials
                correct_username = os.getenv("SWAGGER_USER", "admin")
                correct_password = os.getenv("SWAGGER_PASS", "secret")
                
                if username != correct_username or password != correct_password:
                    return Response("Unauthorized", status_code=401)
                    
            except Exception:
                return Response("Unauthorized", status_code=401)
        
        return await call_next(request)