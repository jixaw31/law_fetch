from fastapi import APIRouter, Request
from typing import List

from app.models.pydantic.user import UserCreate, UserRead, UserUpdate
from app.container import container


router = APIRouter()

# =========================================
# Create a new user
# =========================================
@router.post("/create-user")
async def sign_up(user: UserCreate, request: Request):
    container: Container = request.app.container  # ✅ use request
    session_factory = container.async_postgres_session_factory()
    service = container.user_service()  # also need await if singleton is async
    async with session_factory() as session:
        return await service.create_user(user, session)

# =========================================
# Sign In User
# =========================================
@router.post("/sign-in")
async def sign_in(user: UserCreate, request: Request):
    container: Container = request.app.container
    session_factory = container.async_postgres_session_factory()
    service = container.user_service()  # ✅ await singleton

    async with session_factory() as session:  # ✅ instantiate AsyncSession
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