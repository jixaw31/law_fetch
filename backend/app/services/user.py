from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from fastapi import HTTPException, status
import bcrypt
from qdrant_client import AsyncQdrantClient, models
import os
from dotenv import load_dotenv


from app.models.sql.user import User
from app.utils.jwt_handler import create_access_token

load_dotenv(".env")

class UserService:
    def __init__(
        self, qdrant_client: AsyncQdrantClient,
        # redis_client: Redis,
    ):
        self.client = qdrant_client

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

        # Step 1: Add user to DB and commit
        session.add(user_db)
        try:
            await session.commit()
            await session.refresh(user_db)  # now user_db.id is available
        except IntegrityError as e:
            await session.rollback()
            if "user_name" in str(e.orig):
                raise HTTPException(status_code=400, detail="Username already exists")
            if "email" in str(e.orig):
                raise HTTPException(status_code=400, detail="Email already exists")
            raise
        
        # TODO JUST REPLACE THESE GUYS with One collection,
        print("\n started creating user's collections... \n")
        # Step 2: Create Qdrant collections **after user is committed**
        collection_name = user_db.id

        
        if not await self.client.collection_exists(collection_name):
            await self.client.create_collection(
                collection_name=collection_name,
                vectors_config={
                "dense": models.VectorParams(
                    size=int(os.getenv("EMBEDDING_VECTOR_SIZE")),  # Default to 768 if not set
                    distance=models.Distance.COSINE
                )
                },
                sparse_vectors_config={
                    "sparse": models.SparseVectorParams()
                    # You can add optional parameters:
                    # index=models.SparseIndexParams(on_disk=True)
                }
            )
            
        print("\n user's collections created. \n")
        # Step 3: Return the created user
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

        # TODO CREATE USER'S COLLECTION 

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
