# Investment Platform Backend

API REST desenvolvida com FastAPI para gestão de investimentos.

## 🚀 Tecnologias

- **FastAPI** - Framework web moderno e rápido
- **PostgreSQL** - Banco de dados relacional
- **SQLAlchemy** - ORM para Python
- **Pydantic** - Validação de dados
- **JWT** - Autenticação e autorização
- **Docker** - Containerização

## 💻 Desenvolvimento

### Executar com Docker (Recomendado)
```bash
# Iniciar backend + banco de dados
docker compose up --build

# Parar os serviços
docker compose down

# Ver logs
docker compose logs -f backend
```

### Executar Localmente
```bash
# Instalar dependências
pip install -r backend/requirements.txt

# Configurar variáveis de ambiente
export DATABASE_URL=postgresql+asyncpg://invest:investpw@localhost:5432/investdb

# Executar aplicação
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🌐 URLs dos Serviços

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **API Base**: http://localhost:8000
- **PostgreSQL**: localhost:5432

## 📋 API Endpoints

### 🔐 Autenticação
- `POST /auth/login` - Login de usuário
- `POST /auth/register` - Registro de usuário
- `POST /auth/refresh` - Renovar token

### 👥 Clientes
- `GET /clients` - Listar clientes (com filtros e paginação)
- `POST /clients` - Criar cliente
- `GET /clients/{id}` - Buscar cliente por ID
- `PUT /clients/{id}` - Atualizar cliente
- `DELETE /clients/{id}` - Deletar cliente

### 💰 Ativos
- `GET /assets` - Listar ativos
- `POST /assets` - Criar ativo
- `GET /assets/{id}` - Buscar ativo por ID
- `PUT /assets/{id}` - Atualizar ativo
- `DELETE /assets/{id}` - Deletar ativo

### 📊 Alocações
- `GET /allocations` - Listar alocações
- `POST /allocations` - Criar alocação
- `GET /allocations/{id}` - Buscar alocação por ID
- `PUT /allocations/{id}` - Atualizar alocação
- `DELETE /allocations/{id}` - Deletar alocação
- `GET /allocations/summary` - Resumo de alocações

### 💸 Movimentações
- `GET /movements` - Listar movimentações
- `POST /movements` - Criar movimentação
- `GET /movements/{id}` - Buscar movimentação por ID
- `PUT /movements/{id}` - Atualizar movimentação
- `DELETE /movements/{id}` - Deletar movimentação
- `GET /movements/summary` - Resumo de movimentações

## 📁 Estrutura do Projeto

```
backend/
├── app/
│   ├── main.py              # Aplicação principal
│   ├── models/              # Modelos SQLAlchemy
│   │   ├── user.py
│   │   ├── client.py
│   │   ├── asset.py
│   │   ├── allocation.py
│   │   └── movement.py
│   ├── schemas/             # Schemas Pydantic
│   ├── routers/             # Endpoints da API
│   │   ├── auth.py
│   │   ├── clients.py
│   │   ├── assets.py
│   │   ├── allocations.py
│   │   └── movements.py
│   ├── services/            # Lógica de negócio
│   ├── database.py          # Configuração do banco
│   └── dependencies.py      # Dependências da API
├── requirements.txt         # Dependências Python
└── Dockerfile              # Container configuration
```

## 🔧 Variáveis de Ambiente

```env
DATABASE_URL=postgresql+asyncpg://invest:investpw@db:5432/investdb
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## 🗃️ Banco de Dados

### Modelos Principais
- **Users** - Usuários do sistema
- **Clients** - Clientes da plataforma
- **Assets** - Ativos financeiros
- **Allocations** - Alocações de investimento
- **Movements** - Movimentações financeiras

### Relacionamentos
- Cliente → N Alocações
- Ativo → N Alocações
- Cliente → N Movimentações
- Alocação → Cliente + Ativo

## 🚀 Frontend Integration

Para usar com o frontend:

```bash
# Terminal 1: Backend
cd investment-platform-backend
docker compose up --build

# Terminal 2: Frontend
cd investment-platform-frontend
npm run dev
```

## 🔍 Debugging

### Ver logs do banco
```bash
docker compose logs -f db
```

### Acessar container do backend
```bash
docker compose exec backend bash
```

### Resetar banco de dados
```bash
docker compose down -v
docker compose up --build
```

## 📊 Recursos Implementados

✅ **Sistema completo de autenticação JWT**
✅ **CRUD completo para todas as entidades**
✅ **Filtros e paginação avançados**
✅ **Relacionamentos entre entidades**
✅ **Validação de dados com Pydantic**
✅ **Documentação automática da API**
✅ **Containerização com Docker**
✅ **Estrutura escalável e modular**

---

**API robusta para gestão completa de investimentos e clientes**