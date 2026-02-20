# Guide: PHP / Laravel
<!-- DDD with Laravel, Actions pattern, Pest PHP, PHPStan Level 9 -->

---

## Directory Structure — DDD + Actions Pattern

```
app/
  Domain/                    # Business logic — NO Laravel imports
    User/
      Entities/
        User.php             # Domain entity with invariants
      ValueObjects/
        Email.php            # Typed value object
        UserId.php
      Events/
        UserRegistered.php   # Domain event
      Repositories/
        IUserRepository.php  # Interface — implemented in Infrastructure
      Exceptions/
        EmailAlreadyExistsException.php

  Application/               # Orchestrates domain — Actions pattern
    User/
      CreateUser/
        CreateUserAction.php       # Single-responsibility action
        CreateUserData.php         # Typed DTO (Spatie Laravel Data)
        CreateUserResult.php       # Return DTO
      GetUser/
        GetUserAction.php

  Infrastructure/            # Laravel implementations
    Database/
      User/
        EloquentUserRepository.php # Implements IUserRepository
        UserModel.php              # Eloquent model (infrastructure concern)
      Migrations/
    Mail/
      WelcomeEmail.php
    Queue/
      SendWelcomeEmailJob.php

  Http/                      # Laravel HTTP layer — thin
    Controllers/
      Api/
        UserController.php   # Delegates to Application layer actions
    Requests/
      CreateUserRequest.php  # FormRequest validation
    Resources/
      UserResource.php       # API response formatting (JsonResource)

tests/
  Unit/                      # Domain + Application tests (no DB)
  Feature/                   # HTTP + Database tests (RefreshDatabase)
  Browser/                   # Dusk browser tests (or Pest Browser)
```

---

## AGENTS.md Snippet (Laravel project)

```yaml
runtime: PHP 8.3
language: PHP (typed, strict)
framework: Laravel 11.x
package_manager: Composer 2.x

install: composer install
dev: php artisan serve
test: php artisan test
test_coverage: php artisan test --coverage
test_single: vendor/bin/pest tests/Unit/Domain/UserTest.php
build: composer install --no-dev --optimize-autoloader
typecheck: vendor/bin/phpstan analyse --level=9
lint: vendor/bin/pint --test
format: vendor/bin/pint
security_scan: composer audit
migrate: php artisan migrate
```

---

## Tech Stack

### Core
| Role | Library | Why |
|---|---|---|
| Framework | Laravel 11.x | Full-stack, mature ecosystem |
| DTOs | `spatie/laravel-data` | Typed DTOs with casting + validation |
| State Machine | `spatie/laravel-model-states` | Enum-like states with transitions |
| Query Builder | Eloquent (with Spatie QueryBuilder) | Flexible, typed |
| API docs | Scribe (`knuckleswtf/scribe`) | Auto-generates from controllers |

### Testing
| Role | Library | Command |
|---|---|---|
| Unit + Feature | Pest PHP | `php artisan test` or `vendor/bin/pest` |
| Browser | Pest Browser plugin or Laravel Dusk | `php artisan dusk` |
| Coverage | Xdebug + PCOV | `php artisan test --coverage` |
| HTTP mocking | Laravel's `Http::fake()` | Built-in |

### Security
| Role | Library | Command |
|---|---|---|
| Dep audit | `composer audit` | Built-in Composer 2.4+ |
| SAST/Security | Enlightn | `php artisan enlightn` |
| Static analysis | PHPStan Level 9 | `vendor/bin/phpstan analyse` |
| Vulnerability db | `roave/security-advisories` | Added to composer.json (blocks installs) |
| Secret detection | gitleaks | `gitleaks detect --source=.` |
| Architecture | deptrac | `vendor/bin/deptrac analyse` |

---

## Patterns

### Domain Entity

```php
// app/Domain/User/Entities/User.php
declare(strict_types=1);

namespace App\Domain\User\Entities;

use App\Domain\User\ValueObjects\Email;
use App\Domain\User\ValueObjects\UserId;
use App\Domain\User\Events\UserRegistered;

final class User
{
    /** @var list<object> */
    private array $events = [];

    private function __construct(
        public readonly UserId $id,
        public readonly Email $email,
        public readonly string $name,
        public readonly \DateTimeImmutable $createdAt,
    ) {}

    public static function create(Email $email, string $name): self
    {
        $user = new self(UserId::generate(), $email, $name, new \DateTimeImmutable());
        $user->events[] = new UserRegistered($user->id->value, $user->email->value);
        return $user;
    }

    /** @return list<object> */
    public function releaseEvents(): array
    {
        $events = $this->events;
        $this->events = [];
        return $events;
    }
}
```

### Value Object

```php
// app/Domain/User/ValueObjects/Email.php
declare(strict_types=1);

namespace App\Domain\User\ValueObjects;

use App\Domain\User\Exceptions\InvalidEmailException;

final readonly class Email
{
    public string $value;

    private function __construct(string $value)
    {
        $this->value = $value;
    }

    public static function create(string $value): self
    {
        if (!filter_var($value, FILTER_VALIDATE_EMAIL) || strlen($value) > 255) {
            throw new InvalidEmailException("Invalid email: {$value}");
        }
        return new self(strtolower(trim($value)));
    }

    public function equals(self $other): bool
    {
        return $this->value === $other->value;
    }
}
```

### Typed DTO (Spatie Laravel Data)

```php
// app/Application/User/CreateUser/CreateUserData.php
declare(strict_types=1);

namespace App\Application\User\CreateUser;

use Spatie\LaravelData\Attributes\Validation\Email;
use Spatie\LaravelData\Attributes\Validation\Max;
use Spatie\LaravelData\Attributes\Validation\Min;
use Spatie\LaravelData\Data;

final class CreateUserData extends Data
{
    public function __construct(
        #[Email, Max(255)]
        public readonly string $email,

        #[Min(1), Max(100)]
        public readonly string $name,
    ) {}
}
```

### Single-Responsibility Action

```php
// app/Application/User/CreateUser/CreateUserAction.php
declare(strict_types=1);

namespace App\Application\User\CreateUser;

use App\Domain\User\Entities\User;
use App\Domain\User\Repositories\IUserRepository;
use App\Domain\User\ValueObjects\Email;
use App\Domain\User\Exceptions\EmailAlreadyExistsException;
use Illuminate\Contracts\Events\Dispatcher;

final class CreateUserAction
{
    public function __construct(
        private readonly IUserRepository $userRepository,
        private readonly Dispatcher $eventDispatcher,
    ) {}

    public function execute(CreateUserData $data): CreateUserResult
    {
        $email = Email::create($data->email);

        if ($this->userRepository->findByEmail($email) !== null) {
            throw new EmailAlreadyExistsException($email->value);
        }

        $user = User::create($email, $data->name);
        $this->userRepository->save($user);

        foreach ($user->releaseEvents() as $event) {
            $this->eventDispatcher->dispatch($event);
        }

        return new CreateUserResult(id: $user->id->value);
    }
}
```

### Thin Controller

```php
// app/Http/Controllers/Api/UserController.php
declare(strict_types=1);

namespace App\Http\Controllers\Api;

use App\Application\User\CreateUser\CreateUserAction;
use App\Application\User\CreateUser\CreateUserData;
use App\Http\Resources\UserResource;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

final class UserController
{
    public function store(Request $request, CreateUserAction $action): JsonResponse
    {
        $result = $action->execute(CreateUserData::from($request->validated()));
        return response()->json(['id' => $result->id], 201);
    }
}
```

---

## Security Best Practices

```php
// config/security-headers.php (or via middleware)
// Use spatie/laravel-csp for Content Security Policy

// NEVER: raw user input in queries
$users = DB::select("SELECT * FROM users WHERE email = '{$request->email}'"); // SQL INJECTION!

// CORRECT: Eloquent or parameterized
$user = User::where('email', $request->email)->first();
// OR: parameterized
$users = DB::select('SELECT * FROM users WHERE email = ?', [$request->email]);

// Mass assignment protection
protected $fillable = ['name', 'email']; // Explicit allowlist
// NEVER: protected $guarded = []; (disables protection)

// Rate limiting (in RouteServiceProvider or routes)
Route::middleware(['throttle:5,1'])->group(function () {
    Route::post('/auth/login', [AuthController::class, 'login']);
});
```

---

## Tech Debt Detection

```bash
# PHPStan (type safety) — Level 9 is maximum
vendor/bin/phpstan analyse app/ --level=9

# PHP Mess Detector (complexity, duplication)
vendor/bin/phpmd app/ text cleancode,codesize,controversial,design,naming,unusedcode

# PHP Code Sniffer (code style)
vendor/bin/phpcs --standard=PSR12 app/

# Deptrac (architecture layer enforcement)
vendor/bin/deptrac analyse --config-file deptrac.yaml

# Check for outdated dependencies
composer outdated

# Security vulnerabilities
composer audit
```

---

## deptrac.yaml (Architecture Enforcement)

```yaml
# deptrac.yaml
parameters:
  paths:
    - ./app
  layers:
    - name: Domain
      collectors:
        - type: directory
          value: Domain/.*
    - name: Application
      collectors:
        - type: directory
          value: Application/.*
    - name: Infrastructure
      collectors:
        - type: directory
          value: Infrastructure/.*
    - name: Http
      collectors:
        - type: directory
          value: Http/.*
  ruleset:
    Domain:       # Domain can only depend on itself
      - ~Application
      - ~Infrastructure
      - ~Http
    Application:  # Application can use Domain
      - Domain
    Infrastructure: # Infrastructure implements Domain interfaces
      - Domain
    Http:         # HTTP can use Application (not Domain directly)
      - Application
```
