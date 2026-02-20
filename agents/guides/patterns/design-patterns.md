# Modern Design Patterns Guide (2025 Edition)

This guide covers essential software design patterns, updated for modern distributed and cloud-native contexts.

## 1. Creational Patterns
**Focus**: Object creation mechanisms.

### Factory Method / Abstract Factory
-   **Concept**: Create objects without specifying the exact class.
-   **Modern Use**: LLM Client factories (OpenAI vs Anthropic clients), Cloud SDK initialization.
-   **When to use**: When the implementation needs to be swappable at runtime based on config.

### Builder
-   **Concept**: Construct complex objects step-by-step.
-   **Modern Use**: Constructing complex HTTP requests, prompt chains, or Kubernetes manifests.
-   **When to use**: When an object has >3 optional constructor parameters.

### Singleton
-   **Concept**: Ensure a class has only one instance.
-   **Modern Use**: Database connection pools, Configuration managers, Logging services.
-   **Warning**: Avoid for stateful business logic; it makes testing hard.

## 2. Structural Patterns
**Focus**: Class and object composition.

### Adapter
-   **Concept**: Make incompatible interfaces work together.
-   **Modern Use**: Standardizing different 3rd party APIs (e.g., Stripe vs PayPal) behind a single `PaymentProvider` interface.

### Facade
-   **Concept**: Simple interface to a complex sub-system.
-   **Modern Use**: A `CloudStorage` class that wraps the complexity of S3/GCS SDKs.

### Proxy
-   **Concept**: A placeholder for another object to control access.
-   **Modern Use**: Caching proxies, Lazy loading large datasets, Security/Auth gates.

## 3. Behavioral Patterns
**Focus**: Communication between objects.

### Strategy (The #1 Pattern)
-   **Concept**: Define a family of algorithms, put each in a separate class, and make them interchangeable.
-   **Modern Use**: Search algorithms (Exact vs Vector), Authentication strategies (OAuth vs API Key).
-   **Why strict?**: It eliminates massive `if/else` or `switch` statements.

### Observer / Pub-Sub
-   **Concept**: Notify subscribers of state changes.
-   **Modern Use**: Event-Driven Architecture (receiving logic), UI Reactivity (Redux/MobX).

### Command
-   **Concept**: Turn a request into a stand-alone object.
-   **Modern Use**: Job queues (Sidekiq/Celery tasks), Undo/Redo functionality.

## 4. Cloud & Microservices Patterns

### Circuit Breaker
-   **Problem**: Cascading failures in distributed systems.
-   **Solution**: Stop calling a failing service for a timeout period.
-   **Library**: `Polly` (.NET), `Resilience4j` (Java), `opossum` (Node).

### Sidecar
-   **Problem**: Application logic polluted with infra concerns (logging, mTLS).
-   **Solution**: Run a helper process alongside the main app container.
-   **Example**: Envoy, Istio.

### Backend for Frontend (BFF)
-   **Problem**: One API doesn't fit Mobile, Web, and IoT needs equally.
-   **Solution**: Create separate API gateways for each client type.
