import asyncio
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy import select

async def create_admin_user():
    async with AsyncSessionLocal() as db:
        # Verificar se usuário já existe
        result = await db.execute(select(User).where(User.email == 'admin@test.com'))
        user = result.scalar_one_or_none()
        
        if not user:
            # Criar usuário admin
            user = User(
                email='admin@test.com',
                password=get_password_hash('admin123'),
                is_active=True
            )
            db.add(user)
            await db.commit()
            print('Admin user created successfully')
        else:
            print('Admin user already exists')

if __name__ == "__main__":
    asyncio.run(create_admin_user())