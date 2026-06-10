---
name: performant-php
description: "Strategies for high-performance, modern PHP across the ecosystem (PHP 8.4/8.5, OPcache+JIT, FrankenPHP worker mode, Composer, Symfony & Laravel, PHPStan/Psalm, Pest/PHPUnit)."
triggers: [php, php 8.4, php 8.5, composer, symfony, laravel, frankenphp, opcache, jit, phpstan, psalm, pest, phpunit, php performance]
when_to_use: "Use this when the task involves: php; php 8.4; php 8.5; composer; symfony; laravel; frankenphp; opcache; jit; phpstan."
tags: [coding, php, architecture]
context_cost: medium
---
# Performant PHP Skill

## Goal
Build fast, type-safe, maintainable PHP services using the current ecosystem (versions verified 2026-06-10). This is the language-level companion to `performant-laravel.skill.md`; use it for general PHP, Symfony, and framework-agnostic work.

## Capabilities

### 1. Modern language baseline
- **Target PHP 8.4+ (8.5 current stable).** Use **property hooks** and **asymmetric visibility** (8.4) to remove boilerplate getters/setters; **lazy objects** (8.4) for deferred initialization; PDO driver-specific subclasses. On 8.5, the **pipe operator `|>`** chains callables and the built-in **URI extension** parses/normalizes URLs (RFC 3986 / WHATWG).
- Always `declare(strict_types=1);`. Use `readonly` classes/properties, enums (backed where serialized), first-class callable syntax, and constructor property promotion.

### 2. Runtime performance
- **OPcache** must be enabled in production; tune `opcache.memory_consumption`, `opcache.max_accelerated_files`, and `opcache.validate_timestamps=0` (with deploy-time cache reset).
- **JIT** (available 8.3+) more than doubles throughput on CPU-bound work (benchmarks ~+110%); negligible/negative for typical I/O-bound web requests — enable and measure, don't assume.
- **FrankenPHP worker mode** (Caddy-based app server) keeps the framework booted between requests — large latency wins for Laravel/Symfony; also gives Early Hints and real-time (Mercure). Alternative: RoadRunner or Swoole/OpenSwoole.
- Use `preload` for hot framework classes.

### 3. Database & I/O
- Eliminate N+1: eager-load (Eloquent `with()`, Doctrine fetch joins); add covering indexes; use `EXPLAIN`.
- Stream large results with generators (`yield`) to keep memory constant; chunk batch jobs.
- Cache with Redis (PSR-6/PSR-16); use tags and explicit invalidation; queue slow work (Horizon / Symfony Messenger).

### 4. Type safety & quality gates
- **PHPStan** (aim level 8–9) or **Psalm** for static analysis; **Rector** for automated upgrades/refactors.
- **Pint** / PHP-CS-Fixer (PSR-12) for formatting; **Deptrac** for architectural layer enforcement.
- **composer audit** + `roave/security-advisories` to block vulnerable dependencies.

### 5. Testing
- **Pest** (or PHPUnit) for unit + feature tests; PCOV/Xdebug for coverage; HTTP fakes for external calls; Testcontainers / sqlite-in-memory for integration.

### 6. Frameworks
- **Laravel 12** (min PHP 8.2) — see `performant-laravel.skill.md` for Octane/Eloquent specifics.
- **Symfony 7.4 (LTS, supported to 2028/2029)** — autowiring, attributes, Messenger for async, API Platform for APIs; latest line is Symfony 8.x.

## Steps
1. **Baseline**: profile a representative request (Blackfire / Xdebug profiler / `phpbench`) before changing anything.
2. **Enable OPcache + JIT**, measure, then add worker mode (FrankenPHP/RoadRunner) if request boot dominates.
3. **Kill N+1 and add indexes**; cache the verified-hot, rarely-changing reads.
4. **Raise the static-analysis level** (PHPStan/Psalm) and let it fail CI; apply Rector for safe upgrades.
5. **Re-profile** and record the before/after numbers.

## Sources (verified 2026-06-10)
- PHP 8.5 / 8.4 features: <https://www.php.net/releases/8.5/en.php> · <https://php.watch/versions>
- Laravel 12: <https://laravel.com/docs/12.x/releases>
- Symfony 7.4 LTS: <https://symfony.com/releases>
- FrankenPHP: <https://frankenphp.dev/>
