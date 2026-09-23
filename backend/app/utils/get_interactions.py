import asyncpg
from sqlmodel import select

from typing import List

from app.container import container
# from models.sql import Interaction

async def load_interactions():
    conn = await asyncpg.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="2281249271",
        database="postgres"
    )
    
    try:
        # Fetch all records
        records = await conn.fetch("SELECT id, content, timestamp FROM chat_history ORDER BY timestamp")
        
        # Convert to list of dictionaries (same format as original)
        chat_history = []
        for record in records:
            chat_dict = {
                'id': record['id'],
                'content': record['content'],
                'timestamp': record['timestamp']
            }
            chat_history.append(chat_dict)
        
        return chat_history
        
    finally:
        await conn.close()

async def load_specific_interactions(vector_ids: list, exclude_ids: set):
    """Load only interactions that match your vector IDs"""
    conn = await asyncpg.connect(...)
    
    try:
        # Use SQL IN clause to get only needed IDs
        query = """
            SELECT id, content, timestamp 
            FROM chat_history 
            WHERE id = ANY($1::text[]) 
            AND id != ALL($2::text[])
        """
        records = await conn.fetch(query, vector_ids, list(exclude_ids))
        

        print(records[:2])
        
    finally:
        await conn.close()


async def get_interactions_batch(
    interaction_ids: List[str],
    # session: AsyncSession
) -> List[Interaction]:
    """
    Fetch multiple interactions by their IDs.
    
    Args:
        interaction_ids: List of interaction IDs to fetch
        session: SQLAlchemy async session
    
    Returns:
        List of Interaction objects ordered by timestamp
    """
    # Query using SQLModel's select
    stmt = (
        select(Interaction)
        .where(Interaction.id.in_(interaction_ids))
        .order_by(Interaction.timestamp)
    )
    # async_postgres_session_factory = container.async_postgres_session_factory()
    session_factory = container.async_postgres_session_factory()
    # ✅ Create a session FIRST using the factory
    async with session_factory() as session:  # This creates the session
        result = await session.execute(stmt)  # Now execute on the session
        interactions = result.scalars().all()
    # result = await session_factory.execute(stmt)
    # interactions = result.scalars().all()
    
    return interactions


import asyncio
if __name__ == "__main__":
    asyncio.run(get_interactions_batch())