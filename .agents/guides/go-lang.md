# Guide: Go (Golang)
<!-- Idiomatic Go, Clean Architecture, Echo/Gin, Ent, Testify, Testcontainers -->

---

## Directory Structure — Standard Go Layout (2026)

Adheres to `golang-standards/project-layout` but adapted for Agentic Engineering.

```
cmd/
  api/
    main.go                  # Entry point (DI container, server start)
  worker/
    main.go                  # Background worker entry point

internal/                    # Private application code (Library pattern)
  domain/                    # Pure business logic (structs, interfaces)
    user.go                  # User struct & Repository interfaces
    order.go
    errors.go                # Domain errors

  service/                   # Application Logic (Use Cases)
    user_service.go          # Orchestrate domain + database
    order_service.go

  adapter/                   # Interface Adapters (Driven & Driving)
    handler/
      http/                  # HTTP Handlers (Echo/Gin)
        user_handler.go
    repository/
      ent/                   # Ent ORM implementation
        schema/              # Database Schema Definitions
    grpc/                    # gRPC implementation

  config/                    # Configuration struct (Viper/Env)
  
pkg/                         # Public sharable libraries (Optional)
  logger/                    # structured logger (slog/zap)
  utils/

tests/
  integration/               # Testcontainers integration tests
  e2e/                       # End-to-End API tests

go.mod
go.sum
Makefile
```

---

## Dependency Rules (Idiomatic)

```go
// internal/domain CANNOT import internal/adapter or internal/service
// internal/service CAN import internal/domain
// internal/adapter CAN import internal/domain AND internal/service
// cmd/api CAN import everything (Composition Root)

// CORRECT: Service depends on Repository Interface
type UseCase struct {
    Repo domain.UserRepository
}

// WRONG: Service depends on Ent implementation directly
type UseCase struct {
    Repo *ent.Client // Avoid this coupling in Service layer
}
```

---

## AGENTS.md Snippet (Go project)

```yaml
runtime: Go 1.25+
language: Go (Strict Linting)
framework: Echo v4 / Standard Lib
package_manager: go mod

install: go mod download
dev: air # Live reload
test: go test -v ./...
test_coverage: go test -coverprofile=coverage.out ./...
test_single: go test -v ./internal/service/user_service_test.go
build: go build -o bin/api cmd/api/main.go
lint: golangci-lint run
format: gofumpt -w .
security_scan: govulncheck ./...
migrate: go run -mod=mod entgo.io/ent/cmd/ent generate ./internal/adapter/repository/ent/schema
```

---

## Tech Stack (2026 Recommended)

### Core
| Role | Library | Why |
|---|---|---|
| Runtime | Go 1.25+ | Generic improvements, range-over-func |
| HTTP Framework | **Echo** / **Fiber** | Fast, robust middleware, idiomatic context |
| Router | **Chi** | If employing Standard Lib only (lightweight) |
| ORM / Data | **Ent** | Type-safe graph, code-generation, great for Agents |
| Config | **Koanf** / Viper | Modern configuration management |
| Logging | **Slog** (Std Lib) | Structured logging is now built-in |

### Testing
| Role | Library | Command |
|---|---|---|
| Assertions | **Testify** | `assert.Equal(t, expected, actual)` |
| BDD (Optional) | **Ginkgo** | For complex behavior specs |
| Integration DB | **Testcontainers** | Real Docker Postgres in tests |
| Mocks | **Mockery** | Generate mocks for interfaces |

### Security & Quality
| Role | Library | Command |
|---|---|---|
| Linter | `golangci-lint` | `golangci-lint run` (Aggressive preset) |
| Vuln Scan | `govulncheck` | Native Go vulnerability DB checker |
| API Docs | `swag` | Generate OpenAPI from comments |

---

## Code Patterns

### 1. Domain Entity (Rich Model)

```go
// internal/domain/user.go
package domain

import "errors"

var ErrInvalidEmail = errors.New("invalid email domain")

type User struct {
    ID    string
    Name  string
    Email string
}

// Business Rules can live here
func NewUser(id, name, email string) (*User, error) {
    if email == "" {
        return nil, ErrInvalidEmail
    }
    return &User{ID: id, Name: name, Email: email}, nil
}

type UserRepository interface {
    Save(ctx context.Context, u *User) error
    FindByID(ctx context.Context, id string) (*User, error)
}
```

### 2. Service (Use Case)

```go
// internal/service/user_service.go
package service

import (
    "context"
    "myapp/internal/domain"
)

type UserService struct {
    repo domain.UserRepository
}

func NewUserService(repo domain.UserRepository) *UserService {
    return &UserService{repo: repo}
}

func (s *UserService) Register(ctx context.Context, name, email string) error {
    // 1. Domain Logic
    u, err := domain.NewUser(domain.NewID(), name, email)
    if err != nil {
        return err
    }
    
    // 2. Persist
    return s.repo.Save(ctx, u)
}
```

### 3. HTTP Handler (Echo)

```go
// internal/adapter/handler/http/user_handler.go
package http

import (
    "net/http"
    "github.com/labstack/echo/v4"
)

type UserHandler struct {
    svc *service.UserService
}

func (h *UserHandler) Register(c echo.Context) error {
    var req struct {
        Name  string `json:"name"`
        Email string `json:"email"`
    }
    
    if err := c.Bind(&req); err != nil {
        return c.JSON(http.StatusBadRequest, echo.Map{"error": "bad request"})
    }
    
    if err := h.svc.Register(c.Request().Context(), req.Name, req.Email); err != nil {
        return c.JSON(http.StatusInternalServerError, echo.Map{"error": err.Error()})
    }
    
    return c.NoContent(http.StatusCreated)
}
```

---

## Development Workflow with Agents

### "Scaffold New Feature" prompt:
> "Agent, create a new 'Product' domain entity in `internal/domain`. Then generate the Ent schema, run `go generate`, implement the repository interface in `internal/adapter/repository`, add a `ProductService`, and expose it via a new Echo handler."

### "Test It" prompt:
> "Agent, write a specialized integration test in `tests/integration` using Testcontainers to spin up Postgres, migrate the Ent schema, and verify the `ProductService.Create` flow."

---

## Tech Debt & Maintenance

```bash
# Update dependencies
go get -u ./...
go mod tidy

# Run formatter (stricter than gofmt)
gofumpt -w .

# Linting
golangci-lint run --fix
```
