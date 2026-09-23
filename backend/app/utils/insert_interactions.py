
import  asyncio, json
from typing import Optional, Tuple
from sqlmodel import text, select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.models.my_sql_models import Interaction


class ChatHistoryDeduplicator:
    def __init__(self, engine):
        self.engine = engine
        self.async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
    
    async def ensure_extensions(self):
        """Ensure pg_trgm extension and index exist"""
        async with self.async_session() as session:
            # Create the pg_trgm extension if it doesn't exist
            await session.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
            
            # Create GIN index for fast similarity searches
            await session.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_content_similarity 
                ON interactions USING GIN (content gin_trgm_ops)
            """))
            await session.commit()
    
    async def insert_without_duplicate(
        self, 
        content: str,
        id: str,
        timestamp: int,  # Changed to int based on schema
        user_id: str,    # Added user_id parameter
        similarity_threshold: float = 0.95
    ) -> Tuple[bool, Optional[str]]:
        """
        Insert a message, preventing near-duplicates using pg_trgm
        
        Args:
            content: The message text to insert
            id: Unique identifier for the interaction
            timestamp: Unix timestamp (integer)
            user_id: User ID associated with this interaction
            similarity_threshold: 0.0-1.0, higher = stricter matching
        
        Returns:
            (inserted: bool, id: str | None)
        """
        async with self.async_session() as session:
            async with session.begin():
                # Check for duplicate using raw SQL with pg_trgm
                result = await session.execute(
                    text("""
                        WITH duplicate_check AS (
                            SELECT EXISTS(
                                SELECT 1 FROM interactions 
                                WHERE content % :content 
                                AND similarity(content, :content) > :threshold
                                AND user_id = :user_id
                            ) AS is_duplicate
                        )
                        INSERT INTO interactions (id, content, timestamp, user_id, created_at)
                        SELECT :id, :content, :timestamp, :user_id, CURRENT_TIMESTAMP
                        WHERE NOT (SELECT is_duplicate FROM duplicate_check)
                        RETURNING id
                    """),
                    {
                        "content": content,
                        "threshold": similarity_threshold,
                        "id": id,
                        "timestamp": timestamp,
                        "user_id": user_id
                    }
                )
                
                inserted_id = result.first()
                if inserted_id:
                    await session.commit()
                    return True, inserted_id[0]
                return False, None
    
    async def insert_exact_only(
        self, 
        content: str,
        id: str,
        timestamp: int,
        user_id: str,
    ) -> Tuple[bool, Optional[str]]:
        """
        Insert only if exact duplicate doesn't exist (faster, no fuzzy matching)
        """
        async with self.async_session() as session:
            # Check if exact duplicate exists for this user
            stmt = select(Interaction).where(
                Interaction.content == content,
                Interaction.user_id == user_id
            )
            result = await session.execute(stmt)
            existing = result.first()
            
            if not existing:
                interaction = Interaction(
                    id=id,
                    content=content,
                    timestamp=timestamp,
                    user_id=user_id
                )
                session.add(interaction)
                await session.commit()
                return True, id
            
            return False, None
    
    async def get_similar_messages(
        self,
        content: str,
        user_id: str,
        similarity_threshold: float = 0.7,
        limit: int = 5
    ):
        """Get similar messages for a given content and user"""
        async with self.async_session() as session:
            result = await session.execute(
                text("""
                    SELECT id, content, timestamp, similarity(content, :content) as sim_score
                    FROM interactions
                    WHERE content % :content 
                    AND similarity(content, :content) > :threshold
                    AND user_id = :user_id
                    ORDER BY similarity(content, :content) DESC
                    LIMIT :limit
                """),
                {
                    "content": content,
                    "threshold": similarity_threshold,
                    "user_id": user_id,
                    "limit": limit
                }
            )
            return result.fetchall()


# Usage Example
async def main():
    # Create async engine with asyncpg
    # IMPORTANT: Use postgresql+asyncpg:// not postgresql://
    DATABASE_URL = "postgresql+asyncpg://postgres:2281249271@localhost:5432/postgres"
    
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,  # Set to False in production
        pool_size=10,
        max_overflow=20
    )
    
    # Initialize deduplicator
    deduplicator = ChatHistoryDeduplicator(engine)
    
    # One-time setup (run once at startup)
    await deduplicator.ensure_extensions()
    
    # # Insert with duplicate prevention
    # inserted, msg_id = await deduplicator.insert_without_duplicate(
    #     content="Your long passage text here...",
    #     id=str(uuid.uuid4()),
    #     timestamp=int(datetime.now().timestamp()),
    #     user_id="user_123",
    #     similarity_threshold=0.7
    # )
    
    # if inserted:
    #     print(f"Message inserted with ID: {msg_id}")
    # else:
    #     print("Duplicate detected - message not inserted")
    with open("app/interactions.json", "r") as f:
        interactions = json.load(f)

    for inter in interactions:
        
        inserted_exact, msg_id_exact = await deduplicator.insert_exact_only(
            content=inter['content'],
            id=inter['id'],
            timestamp=inter['timestamp'],
            user_id="847f5e78-25b0-46b0-8188-1ebefd9c2772" # hardcoded for now
        )
    
    # Clean up
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())