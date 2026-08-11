# Quelyra Empty Skeleton Implementation Plan

> **For the project owner:** This plan deliberately creates names and boundaries only. Implement each milestone later with tests and review checkpoints.

**Goal:** Create a standards-aligned Python, Go, and Vue 3 monorepo skeleton for Quelyra without implementation code or installed dependencies.

**Architecture:** The monorepo separates the Vue workspace, Python FastAPI/LangGraph agent service, and Go query gateway. Shared API contracts, evaluation assets, demos, deployment configuration, and architecture documentation remain top-level concerns.

**Tech Stack:** Python/FastAPI/LangGraph, Go/Gin, Vue 3/Vite/TypeScript, PostgreSQL, Redis, Docker Compose, OpenAPI.

---

### Task 1: Establish repository boundaries

**Files:** root documentation, environment templates, CI placeholder, deployment placeholders, and shared contract placeholders.

- Create only comment-bearing placeholders.
- Keep strict JSON files as empty objects so editors can parse them.
- Do not initialize Git or install dependencies.

### Task 2: Establish Python service boundaries

**Files:** `services/agent-api/src/quelyra_agent/**` and `services/agent-api/tests/**`.

- Separate entrypoints, HTTP API, domain, orchestration graphs, services, clients, repositories, and persistence.
- Keep every Python file comment-only; no imports, classes, functions, or executable statements.

### Task 3: Establish Go gateway boundaries

**Files:** `services/query-gateway/cmd/**`, `services/query-gateway/internal/**`, and gateway tests.

- Use `cmd` and compiler-enforced `internal` boundaries.
- Separate HTTP adapters, use cases, domain, database connectors, policy enforcement, credentials, persistence, artifacts, and audit.
- Keep every Go file comment-only; no package declarations or executable statements.

### Task 4: Establish Vue application boundaries

**Files:** `apps/web/src/**` and frontend tests.

- Use Vue 3, Vite, TypeScript, Router, and Pinia-oriented names.
- Separate reusable components from business features, views, stores, API clients, types, and styles.
- Keep TypeScript and Vue files comment-only; JSON configuration files remain `{}`.

### Task 5: Verify skeleton-only constraints

- Enumerate all directories and files.
- Verify required entrypoints and major boundaries exist.
- Scan `.py`, `.go`, `.ts`, `.vue`, `.yaml`, `.yml`, `.toml`, and shell/build placeholders for non-comment implementation content.
- Do not run builds or tests: this skeleton is intentionally non-runnable until the first implementation milestone.
