"""
Database helpers for hybrid sync/async operations
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import TypeVar, Type, Any, Optional, List

T = TypeVar('T')

class DBHelper:
    """Helper class to abstract sync/async database operations"""
    
    @staticmethod
    async def add_and_commit(db, obj):
        """Add object and commit (hybrid sync/async)"""
        db.add(obj)
        if isinstance(db, AsyncSession):
            await db.commit()
            await db.refresh(obj)
        else:
            db.commit()
            db.refresh(obj)
        return obj
    
    @staticmethod
    async def commit(db):
        """Commit changes (hybrid sync/async)"""
        if isinstance(db, AsyncSession):
            await db.commit()
        else:
            db.commit()
    
    @staticmethod
    async def refresh(db, obj):
        """Refresh object (hybrid sync/async)"""
        if isinstance(db, AsyncSession):
            await db.refresh(obj)
        else:
            db.refresh(obj)
    
    @staticmethod
    async def get_all(db, model: Type[T]) -> List[T]:
        """Get all records (hybrid sync/async)"""
        if isinstance(db, AsyncSession):
            result = await db.execute(select(model))
            return result.scalars().all()
        else:
            result = db.execute(select(model))
            return result.scalars().all()
    
    @staticmethod
    async def get_by_id(db, model: Type[T], obj_id: int) -> Optional[T]:
        """Get object by ID (hybrid sync/async)"""
        if isinstance(db, AsyncSession):
            result = await db.execute(select(model).where(model.id == obj_id))
            return result.scalar_one_or_none()
        else:
            result = db.execute(select(model).where(model.id == obj_id))
            return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_filter(db, model: Type[T], **filters) -> List[T]:
        """Get objects by filters (hybrid sync/async)"""
        query = select(model)
        for key, value in filters.items():
            query = query.where(getattr(model, key) == value)
        
        if isinstance(db, AsyncSession):
            result = await db.execute(query)
            return result.scalars().all()
        else:
            result = db.execute(query)
            return result.scalars().all()
    
    @staticmethod
    async def delete_obj(db, obj):
        """Delete object (hybrid sync/async)"""
        if isinstance(db, AsyncSession):
            await db.delete(obj)
            await db.commit()
        else:
            db.delete(obj)
            db.commit()
    
    @staticmethod
    async def execute_query(db, query):
        """Execute custom query (hybrid sync/async)"""
        if isinstance(db, AsyncSession):
            return await db.execute(query)
        else:
            return db.execute(query)