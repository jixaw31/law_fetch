# from fastapi import Depends, HTTPException, status
# from fastapi.security import HTTPBasic, HTTPBasicCredentials

# import os

# security = HTTPBasic()

# def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
#     correct_username = os.getenv("SWAGGER_USER", "admin")
#     correct_password = os.getenv("SWAGGER_PASS", "secret")
#     if not (credentials.username == correct_username and credentials.password == correct_password):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Unauthorized",
#             headers={"WWW-Authenticate": "Basic"},
#         )
#     return True