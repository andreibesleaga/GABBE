# Guide: Python / FastAPI / AI
<!-- Clean Architecture with Python 3.12+, FastAPI, SQLAlchemy, Pydantic, and AI Agents -->

---

## Directory Structure — Clean Architecture

```
src/
  domain/                    # Pure business logic — NO framework imports
    entities/                # user.py, order.py — domain entities (Pydantic/Dataclasses)
    value_objects/           # email.py, money.py — immutable primitives
    events/                  # user_registered.py — domain events
    ports/                   # i_user_repository.py — interfaces only (Protocol)
    exceptions/              # domain_error.py — base exceptions
    services/                # Pure domain services

  application/               # Use cases — orchestrates domain
    users/
      create_user_use_case.py
      create_user_command.py
      create_user_result.py

  adapters/                  # Interface adapters
    api/                     # FastAPI routers & controllers
      users_router.py
      users_schema.py        # Pydantic schemas for request/response
    presenters/              # Formatters

  infrastructure/            # Framework + external services
    database/
      sqlalchemy_user_repository.py
    llm/                     # AI Model implementations
      openai_service.py
      langchain_adapter.py
    vector_store/
      qdrant_service.py

  main/                      # Composition root
    container.py             # Dependency Injection (Dependency Injector or fast_depends)
    main.py                  # FastAPI app entrypoint

tests/
  unit/                      # Fast, no I/O
  integration/               # Docker containers (Testcontainers)
  e2e/                       # Full API tests
```

---

## Layer Import Rules

```python
# domain/ — MUST NOT import from any other layer
# application/ — MAY import from domain only
# adapters/ — MAY import from domain + application
# infrastructure/ — MAY import from domain (implements interfaces)
# main/ — MAY import from all layers (composition root)

# CORRECT: infrastructure depends on domain interface
from src.domain.ports.i_user_repository import IUserRepository

# WRONG: domain depending on infrastructure
from src.infrastructure.database.models import UserModel # NEVER in domain
```

**Enforce with:** `import-linter`

---

## AGENTS.md Snippet (Python Project)

```yaml
runtime: Python 3.12+
language: Python (Strict Typing)
framework: FastAPI
package_manager: uv (preferred) | poetry

install: uv sync
dev: uv run fastapi dev src/main/main.py
test: uv run pytest
test_coverage: uv run pytest --cov=src
test_single: uv run pytest tests/path/to/test.py
typecheck: uv run mypy src
lint: uv run ruff check src
format: uv run ruff format src
security_scan: uv run bandit -r src
migrate: uv run alembic upgrade head
```

---

## Tech Stack

### Core
| Role | Library | Why |
|---|---|---|
| Runtime | Python 3.12+ | Performance improvements, better typing |
| Web Framework | FastAPI | Async, Pydantic integration, auto-docs |
| Validation | Pydantic v2 | Rust-based speed, strict validation |
| ORM | SQLAlchemy 2.0 | Async support, robust |
| Dependency Inj. | `fast_depends` / `dishka` | Decoupling layers |

### AI / Agentic
| Role | Library | Why |
|---|---|---|
| Orchestration | LangChain / LangGraph | State management, tool calling |
| LLM Client | `openai` / `anthropic` | Official SDKs |
| Vector DB | Qdrant / Chroma | Efficient similarity search |
| Evaluation | Ragas / DeepEval | RAG pipeline evaluation |
| Tracing | LangSmith / Arize Phoenix | Observability for chains |

### Testing & Quality
| Role | Library | Command |
|---|---|---|
| Test Runner | Pytest | `pytest` |
| Integration | Testcontainers | Real DB/service tests in Docker |
| Linting | Ruff | `ruff check` (Replacing Flake8/Isort) |
| Type Checking | Mypy | `mypy --strict` |
| Mutation Test | Mutmut | Verify test quality |

---

## Patterns

### Domain Entity (Pydantic v2)

```python
# src/domain/entities/user.py
from pydantic import BaseModel, Field, EmailStr
from uuid import UUID, uuid4
from datetime import datetime

class User(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    email: EmailStr
    name: str = Field(min_length=1)
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        frozen = True # Immutable pattern
```

### Protocol (Interface)

```python
# src/domain/ports/i_user_repository.py
from typing import Protocol
from src.domain.entities.user import User

class IUserRepository(Protocol):
    async def save(self, user: User) -> None:
        ...

    async def find_by_email(self, email: str) -> User | None:
        ...
```

### Use Case

```python
# src/application/users/create_user_use_case.py
from dataclasses import dataclass
from src.domain.ports.i_user_repository import IUserRepository
from src.domain.entities.user import User

@dataclass
class CreateUserCommand:
    email: str
    name: str

class CreateUserUseCase:
    def __init__(self, repo: IUserRepository):
        self.repo = repo

    async def execute(self, command: CreateUserCommand) -> User:
        # Business rules
        existing = await self.repo.find_by_email(command.email)
        if existing:
            raise ValueError("Email already exists")
        
        user = User(email=command.email, name=command.name)
        await self.repo.save(user)
        return user
```

### FastAPI Router (Adapter)

```python
# src/adapters/api/users_router.py
from fastapi import APIRouter, Depends
from typing import Annotated
from src.main.container import get_create_user_use_case
from src.application.users.create_user_use_case import CreateUserUseCase, CreateUserCommand

router = APIRouter()

@router.post("/users")
async def create_user(
    cmd: CreateUserCommand,
    use_case: Annotated[CreateUserUseCase, Depends(get_create_user_use_case)]
):
    try:
        user = await use_case.execute(cmd)
        return {"id": str(user.id), "email": user.email}
    except ValueError as e:
        return {"error": str(e)}, 400
```

---

## AI Agent Specifics

### Tool Definition Pattern
When exposing tools to LLMs (Function Calling):

```python
# src/infrastructure/llm/tools/calculator.py
from pydantic import BaseModel, Field
from typing import Callable

class AddInput(BaseModel):
    a: int = Field(..., description="First number")
    b: int = Field(..., description="Second number")

def add(a: int, b: int) -> int:
    """Adds two numbers."""
    return a + b

# LangChain / OpenAI format
tool_definition = {
    "type": "function",
    "function": {
        "name": "add",
        "description": "Adds two numbers",
        "parameters": AddInput.model_json_schema()
    }
}
```

### RAG implementation Tip
Keep embedding logic in `infrastructure`:

```python
# src/infrastructure/vector_store/qdrant_service.py
class QdrantRetrievalService(IRetrievalService):
    def __init__(self, client: QdrantClient, verify_ssl: bool = True):
        self.client = client
        # ... implementation details ...
```
