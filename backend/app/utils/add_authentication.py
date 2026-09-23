async def add_authentication():
    import subprocess
    import textwrap

    CONTAINER = "llm_sandbox"

    code = textwrap.dedent('''\
    from fastapi import APIRouter, Request
    from typing import List

    from app.schemas.user import UserCreate, UserRead, UserUpdate
    from app.container import container


    router = APIRouter()

    # =========================================
    # Create a new user
    # =========================================
    @router.post("/create-user")
    async def sign_up(user: UserCreate, request: Request):
        container: Container = request.app.container
        session_factory = container.async_postgres_session_factory()
        service = container.user_service()
        async with session_factory() as session:
            return await service.create_user(user, session)

    # =========================================
    # Sign In User
    # =========================================
    @router.post("/sign-in")
    async def sign_in(user: UserCreate, request: Request):
        container: Container = request.app.container
        session_factory = container.async_postgres_session_factory()
        service = container.user_service()

        async with session_factory() as session:
            return await service.sign_in(user, session, container)


    # =========================================
    # List all users
    # =========================================
    @router.get("/", response_model=List[UserRead])
    async def list_users(request: Request, offset: int = 0, limit: int = 100):
        container: Container = request.app.container
        session_factory = container.async_postgres_session_factory()
        service = container.user_service()

        async with session_factory() as session:
            return await service.list_users(session, offset, limit)


    # =========================================
    # Get a single user by ID
    # =========================================
    @router.get("/users/{user_id}", response_model=UserRead)
    async def get_user(user_id: str, request: Request):
        container: Container = request.app.container
        session_factory = container.async_postgres_session_factory()
        service = container.user_service()

        async with session_factory() as session:
            return await service.get_user(user_id, session)


    # =========================================
    # Update a user's information
    # =========================================
    @router.patch("/update-user/{user_id}", response_model=UserRead)
    async def update_user(user_id: str, user_update: UserUpdate, request: Request):
        container: Container = request.app.container
        session_factory = container.async_postgres_session_factory()
        service = container.user_service()

        async with session_factory() as session:
            return await service.update_user(user_id, user_update, session)


    # =========================================
    # Delete a user by ID
    # =========================================
    @router.delete("/{user_id}")
    async def delete_user(user_id: str, request: Request):
        container: Container = request.app.container
        session_factory = container.async_postgres_session_factory()
        service = container.user_service()

        async with session_factory() as session:
            return await service.delete_user(user_id, session)
    ''')

    subprocess.run(
        ["docker", "exec", CONTAINER, "bash", "-c", f"cat > /workspace/app/api/v1/users.py << 'EOF'\n{code}\nEOF"],
        check=True,
    )

    print("✅ /workspace/app/api/v1/users.py created successfully.")


async def setup_container():
    import subprocess
    import tempfile
    import os

    CONTAINER = "llm_sandbox"

    # Install dependency-injector
    subprocess.run(
        ["docker", "exec", CONTAINER, "pip", "install", "dependency-injector"],
        check=True,
    )
    print("✅ dependency-injector installed.")

    code = '''from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.app.services.user import UserService
from dotenv import load_dotenv
import os

load_dotenv("/workspace/app/.env")

ASYNC_DB_URI = os.getenv("ASYNC_DB_URI")

class Container(containers.DeclarativeContainer):
    # Engine
    async_postgres_engine = providers.Singleton(
        create_async_engine,
        ASYNC_DB_URI,
        echo=True,
    )

    # Session factory
    async_postgres_session_factory = providers.Singleton(
        sessionmaker,
        bind=async_postgres_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Services
    user_service = providers.Singleton(
        UserService,
    )

# Create container instance
container = Container()

# Initialize resources (optional but good practice)
container.init_resources()
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        tmp_path = f.name

    try:
        subprocess.run(
            ["docker", "cp", tmp_path, f"{CONTAINER}:/workspace/app/container.py"],
            check=True,
        )
        print("✅ /workspace/app/container.py created successfully.")
    finally:
        os.unlink(tmp_path)

async def add_user_schemas():
    import subprocess
    import tempfile
    import os

    CONTAINER = "llm_sandbox"

    code = '''from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime, timezone
import uuid


# --------------------
# User-related models
# --------------------

class UserCreate(BaseModel):
    """
    Data model for creating a new user.
    """
    user_name: Optional[str] = Field(default_factory=lambda: f"dear_guest_{str(uuid.uuid4())[:24]}")
    password: str
    email: Optional[EmailStr] = None


class UserRead(BaseModel):
    """
    Data model for reading user information.
    """
    id: str
    user_name: str
    email: Optional[EmailStr] = None

    # Optional personal info
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    country: Optional[str] = None
    bio: Optional[str] = None


class UserUpdate(BaseModel):
    """
    Data model for updating user information.
    """
    user_name: Optional[str] = None
    password: Optional[str] = None
    email: Optional[EmailStr] = None

    # Optional personal info
    first_name: Optional[str] = None
    middle_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    country: Optional[str] = None
    bio: Optional[str] = None
'''

    # Ensure directory exists
    subprocess.run(
        ["docker", "exec", CONTAINER, "mkdir", "-p", "/workspace/app/schemas"],
        check=True,
    )

    # Create __init__.py if not exists
    subprocess.run(
        ["docker", "exec", CONTAINER, "touch", "/workspace/app/schemas/__init__.py"],
        check=True,
    )

    # Write the file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        tmp_path = f.name

    try:
        subprocess.run(
            ["docker", "cp", tmp_path, f"{CONTAINER}:/workspace/app/schemas/user.py"],
            check=True,
        )
        print("✅ /workspace/app/schemas/user.py created successfully.")
    finally:
        os.unlink(tmp_path)


async def add_user_service():
    import subprocess
    import tempfile
    import os

    CONTAINER = "llm_sandbox"

    code = '''from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from fastapi import HTTPException, status
import bcrypt
from dotenv import load_dotenv

from app.models.user import User
from app.app.utils.jwt_handler import create_access_token

load_dotenv(".env")

class UserService:
    def __init__(self):
        pass

    async def create_user(self, user_data, session):
        if not user_data.password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is required"
            )

        # Hash the password
        hashed_password = bcrypt.hashpw(
            user_data.password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        # Create User object
        user_db = User(
            user_name=user_data.user_name,
            hashed_password=hashed_password,
            email=user_data.email
        )

        # Add user to DB and commit
        session.add(user_db)
        try:
            await session.commit()
            await session.refresh(user_db)
        except IntegrityError as e:
            await session.rollback()
            if "user_name" in str(e.orig):
                raise HTTPException(status_code=400, detail="Username already exists")
            if "email" in str(e.orig):
                raise HTTPException(status_code=400, detail="Email already exists")
            raise

        return user_db

    async def sign_in(self, login_data, session, container):
        """
        Sign in a user using username and password, return JWT token.
        login_data should have attributes: user_name, password
        """
        if not login_data.user_name or not login_data.password:
            raise HTTPException(status_code=400, detail="Username and password are required")

        result = await session.execute(select(User).where(User.user_name == login_data.user_name))
        db_user = result.scalar_one_or_none()

        if not db_user or not bcrypt.checkpw(
            login_data.password.encode("utf-8"), 
            db_user.hashed_password.encode("utf-8")
        ):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_access_token({"sub": db_user.user_name})

        return {
            "access_token": token,
            "token_type": "bearer",
            "id": db_user.id,
            "user_name": db_user.user_name,
        }
    
    async def list_users(self, session, offset=0, limit=100):
        result = await session.execute(select(User).offset(offset).limit(limit))
        return result.scalars().all()

    async def get_user(self, user_id: str, session):
        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    async def update_user(self, user_id: str, user_update, session):
        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user_update.user_name is not None:
            user.user_name = user_update.user_name
        if user_update.password is not None:
            user.hashed_password = bcrypt.hashpw(
                user_update.password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")
        if user_update.email is not None:
            user.email = user_update.email

        await session.commit()
        await session.refresh(user)
        return user

    async def delete_user(self, user_id: str, session):
        user = await session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        await session.delete(user)
        await session.commit()
        return {"message": f"User with ID: {user_id} deleted successfully."}
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        tmp_path = f.name

    try:
        subprocess.run(
            ["docker", "cp", tmp_path, f"{CONTAINER}:/workspace/app/services/user.py"],
            check=True,
        )
        print("✅ /workspace/app/services/user.py created successfully.")
    finally:
        os.unlink(tmp_path)


async def add_main():
    import subprocess
    import tempfile
    import os

    CONTAINER = "llm_sandbox"

    code = '''from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.users import router as user_router
from app.app.utils.native_auth import SwaggerAuthMiddleware
from app.schemas.user import *
from app.container import container
from sqlalchemy.ext.asyncio import AsyncEngine
from app.db.session import engine
from app.db.base import *          # registers models
# from app.models.base import Base   # DeclarativeBase
from app.db.init import init_db


container.wire(
    modules=[
        "app.api.v1.users",
    ]
)


# Define lifespan for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize resources
    print("Initializing container resources...")
    container.init_resources()
    await init_db()
    print("Container resources initialized successfully!")
    
    yield  # This is where the app runs
    
    # Shutdown: Clean up resources if needed
    print("Shutting down container resources...")
    # Add any cleanup code here if needed


# Create FastAPI app with lifespan
app = FastAPI(
    title="LangChain API",
    description="Online Store App",
    version="1.0.0",
    lifespan=lifespan
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           # List of allowed origins
    allow_credentials=True,          # Allow cookies/auth headers
    allow_methods=["*"],             # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],             # Allow all headers
    expose_headers=["*"],            # Expose all headers to client
    max_age=3600,                    # Cache preflight requests for 1 hour
)
app.add_middleware(SwaggerAuthMiddleware)

app.container = container

# Include the WebSocket router
app.include_router(user_router, prefix="/api/auth")
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        tmp_path = f.name

    try:
        subprocess.run(
            ["docker", "cp", tmp_path, f"{CONTAINER}:/workspace/app/main.py"],
            check=True,
        )
        print("✅ /workspace/app/main.py created successfully.")
    finally:
        os.unlink(tmp_path)
add_user_service
async def add_native_auth():
    import subprocess
    import tempfile
    import os

    CONTAINER = "llm_sandbox"

    # Ensure directory exists
    subprocess.run(
        ["docker", "exec", CONTAINER, "mkdir", "-p", "/workspace/app/utils"],
        check=True,
    )

    # Create __init__.py if not exists
    subprocess.run(
        ["docker", "exec", CONTAINER, "touch", "/workspace/app/utils/__init__.py"],
        check=True,
    )

    code = '''from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import base64
import os
from dotenv import load_dotenv

load_dotenv("/workspace/app/.env")
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
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        tmp_path = f.name

    try:
        subprocess.run(
            ["docker", "cp", tmp_path, f"{CONTAINER}:/workspace/app/utils/native_auth.py"],
            check=True,
        )
        print("✅ /workspace/app/utils/native_auth.py created successfully.")
    finally:
        os.unlink(tmp_path)

async def add_user_model():
    import subprocess
    import tempfile
    import os

    CONTAINER = "llm_sandbox"

    # Ensure directory exists
    subprocess.run(
        ["docker", "exec", CONTAINER, "mkdir", "-p", "/workspace/app/models"],
        check=True,
    )

    # Create __init__.py if not exists
    subprocess.run(
        ["docker", "exec", CONTAINER, "touch", "/workspace/app/models/__init__.py"],
        check=True,
    )

    code = '''from sqlmodel import SQLModel, Field
from typing import Optional
import uuid


class User(SQLModel, table=True):
    """
    User table/model.
    """
    __tablename__ = "users"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_name: str = Field(index=True, max_length=24, unique=True)
    hashed_password: str
    email: Optional[str] = Field(default=None, index=True)
    
    # Optional personal info
    first_name: Optional[str] = Field(default=None, max_length=50)
    middle_name: Optional[str] = Field(default=None, max_length=50)
    last_name: Optional[str] = Field(default=None, max_length=50)
    age: Optional[int] = Field(default=None)
    phone_number: Optional[str] = Field(default=None, max_length=20)
    address: Optional[str] = Field(default=None, max_length=200)
    bio: Optional[str] = Field(default=None, max_length=500)
    city: Optional[str] = Field(default=None, max_length=100)
    province: Optional[str] = Field(default=None, max_length=100)
    country: Optional[str] = Field(default=None, max_length=100)
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        tmp_path = f.name

    try:
        subprocess.run(
            ["docker", "cp", tmp_path, f"{CONTAINER}:/workspace/app/models/user.py"],
            check=True,
        )
        print("✅ /workspace/app/models/user.py created successfully.")
    finally:
        os.unlink(tmp_path)


async def add_jwt_handler():
    import subprocess
    import tempfile
    import os

    CONTAINER = "llm_sandbox"

    # Ensure directory exists
    subprocess.run(
        ["docker", "exec", CONTAINER, "mkdir", "-p", "/workspace/app/utils"],
        check=True,
    )

    # Create __init__.py if not exists
    subprocess.run(
        ["docker", "exec", CONTAINER, "touch", "/workspace/app/utils/__init__.py"],
        check=True,
    )

    code = '''from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone

SECRET_KEY = "your-super-secret-key"  # Ideally use env vars
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        tmp_path = f.name

    try:
        subprocess.run(
            ["docker", "cp", tmp_path, f"{CONTAINER}:/workspace/app/utils/jwt_handler.py"],
            check=True,
        )
        print("✅ /workspace/app/utils/jwt_handler.py created successfully.")
    finally:
        os.unlink(tmp_path)

async def add_db_base():
    import subprocess
    import tempfile
    import os

    CONTAINER = "llm_sandbox"

    code = '''from sqlmodel import SQLModel
from app.models.user import User

# Import all models here for SQLModel to discover them
# This ensures all tables are created when using SQLModel.metadata.create_all()

__all__ = ["User"]
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        tmp_path = f.name

    try:
        subprocess.run(
            ["docker", "cp", tmp_path, f"{CONTAINER}:/workspace/app/db/base.py"],
            check=True,
        )
        print("✅ /workspace/app/db/base.py created successfully.")
    finally:
        os.unlink(tmp_path)


async def add_db_session():
    import subprocess
    import tempfile
    import os

    CONTAINER = "llm_sandbox"

    code = '''from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv("/workspace/app/.env")

# Create async engine
engine = create_async_engine(os.getenv("ASYNC_DB_URI"), echo=True)

'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        tmp_path = f.name

    try:
        subprocess.run(
            ["docker", "cp", tmp_path, f"{CONTAINER}:/workspace/app/db/session.py"],
            check=True,
        )
        print("✅ /workspace/app/db/session.py created successfully.")
    finally:
        os.unlink(tmp_path)

    
async def add_db_init():
    import subprocess
    import tempfile
    import os

    CONTAINER = "llm_sandbox"

    code = '''from sqlmodel import SQLModel

import app.models.user

from app.container import container


async def init_db():
    engine = container.async_postgres_engine()

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
'''

    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        tmp_path = f.name

    try:
        subprocess.run(
            ["docker", "cp", tmp_path, f"{CONTAINER}:/workspace/app/db/init.py"],
            check=True,
        )
        print("✅ /workspace/app/db/init.py created successfully.")
    finally:
        os.unlink(tmp_path)



async def main():
    await add_authentication()
    await setup_container()
    await add_user_schemas()
    await add_user_service()
    await add_main()
    await add_native_auth()
    await add_user_model()
    await add_jwt_handler()
    await add_db_base()
    await add_db_session()
    await add_db_init()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())