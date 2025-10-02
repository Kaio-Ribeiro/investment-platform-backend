import asyncio
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy import select

async def update_admin_password():
    async with AsyncSessionLocal() as db:
        # Buscar usuário admin
        result = await db.execute(select(User).where(User.email == 'admin@test.com'))
        user = result.scalar_one_or_none()
        
        if user:
            # Atualizar senha
            user.password = get_password_hash('admin123')
            await db.commit()
            print('Admin password updated successfully')
        else:
            print('Admin user not found')

if __name__ == "__main__":
    asyncio.run(update_admin_password())