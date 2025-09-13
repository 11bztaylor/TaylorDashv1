# 🌌 TaylorDash — Visual, Add-Only Mission Control for Your Home Lab

**Local-only. Dockerized. Event-driven.**

A visual-first "second brain" for building and finishing home-lab projects with AI assistants. TaylorDash gives you a blank, pluggable dashboard, a React Flow canvas, and a modular backend that you extend without touching the core (add-only).

<p align="center">
  <img alt="TaylorDash banner" src="docs/_media/banner.png" width="780">
</p>

<p align="center">
  <a href="#"><img alt="Status" src="https://img.shields.io/badge/status-alpha-6E7F5D"></a>
  <a href="#"><img alt="License" src="https://img.shields.io/badge/license-Apache--2.0-0B3B2E"></a>
  <a href="#"><img alt="Docs" src="https://img.shields.io/badge/docs-Diátaxis-2F4F1D"></a>
  <a href="#"><img alt="Conventional Commits" src="https://img.shields.io/badge/commit_style-Conventional%20Commits-355E3B"></a>
</p>

## ✨ What is TaylorDash?

TaylorDash is a visual project command center. You describe what you want; the system renders it as connected components on a canvas, tracks progress and tasks, and ties in "HUD-style" widgets you can dock, drag, and persist. It's architected to be add-only: new features bolt on via adapters, plugins, and events without risky core edits.

- **Add-only frame**: evolve by adding adapters, views, and event consumers—no core rewrites.
- **Visual-first**: flowcharts + draggable widgets; multiple views/tabs for different perspectives.
- **Local-only**: everything runs via [Docker Compose](https://docs.docker.com/compose/) on a single node.
- **Standards-aligned**: [Diátaxis](https://diataxis.fr/) docs, [Conventional Commits](https://conventionalcommits.org/) + SemVer, OTel + Prometheus, [MQTT](https://mosquitto.org/).

## 🧠 Core Ideas

- **Event bus at the center** ([MQTT](https://mosquitto.org/)) → decoupled producers/consumers, easy fan-out, offline-friendly.
- **Observability from Day-1** with [OpenTelemetry](https://opentelemetry.io/) (traces/logs/metrics) → [Prometheus](https://prometheus.io/) scrapes `/metrics`.
- **Security is not an afterthought**: [Keycloak](https://www.keycloak.org/) OIDC (roles: admin/maintainer/viewer), Traefik TLS/HSTS, no secrets in Git.
- **Right storage for the job**: Postgres for metadata/events; TSDB for time-series (default [VictoriaMetrics](https://docs.victoriametrics.com/); Timescale optional).
- **Add-only UI**: plugin routes and a Midnight HUD example (draggable glass widgets with persisted state).
- **Docs that scale**: [Diátaxis](https://diataxis.fr/) split (tutorials / how-tos / reference / explanation).

## 🏗️ System Architecture & Design Patterns

TaylorDash implements an **event-driven, add-only architecture** with microservice patterns optimized for single-node deployment. The system prioritizes extensibility, observability, and security through carefully chosen design patterns.

### 🎯 Core Architectural Principles

- **Add-Only Philosophy**: Extend functionality through adapters, plugins, and event consumers—never modify core components
- **Event-Driven Communication**: MQTT message bus enables loose coupling and offline resilience
- **Observability-First**: OpenTelemetry instrumentation from day one with comprehensive metrics
- **Security by Design**: OIDC authentication, RBAC authorization, and plugin sandboxing
- **Local-First**: Complete functionality without external dependencies post-setup

### 🏛️ Architecture Overview (Phase-1)

```mermaid
graph TB
    subgraph "Edge Layer"
        TF[Traefik<br/>TLS Termination<br/>Security Headers]
    end

    subgraph "Frontend Layer"
        FE[React Frontend<br/>Context API<br/>Plugin Router]
        PL[Plugin Iframes<br/>Sandboxed Execution]
    end

    subgraph "Backend Layer"
        API[FastAPI Backend<br/>Async/Await<br/>Dependency Injection]
        AUTH[Authentication<br/>JWT + RBAC]
    end

    subgraph "Event Layer"
        MQTT[Mosquitto MQTT<br/>Event Bus<br/>Pub/Sub Pattern]
    end

    subgraph "Storage Layer"
        PG[PostgreSQL<br/>Metadata + Events<br/>ACID Transactions]
        TS[VictoriaMetrics<br/>Time-Series Data<br/>Metrics Storage]
        OBJ[MinIO<br/>Object Storage<br/>Versioned Artifacts]
    end

    subgraph "Security Layer"
        KC[Keycloak<br/>OIDC Provider<br/>Identity Management]
    end

    subgraph "Observability Layer"
        PROM[Prometheus<br/>Metrics Collection]
        OTEL[OpenTelemetry<br/>Traces + Logs]
    end

    TF --> FE
    TF --> API
    FE --> PL
    API --> AUTH
    API --> MQTT
    API --> PG
    API --> TS
    API --> OBJ
    AUTH --> KC
    API --> OTEL
    PROM --> API

    style TF fill:#2d3748,stroke:#4a5568,color:#fff
    style MQTT fill:#e53e3e,stroke:#c53030,color:#fff
    style API fill:#3182ce,stroke:#2c5282,color:#fff
    style PG fill:#38a169,stroke:#2f855a,color:#fff
```

### 🎨 Design Patterns & Implementation

#### **1. Event-Driven Architecture Pattern**
- **Implementation**: MQTT message bus with JSON event contracts
- **Benefits**: Loose coupling, horizontal scalability, offline resilience
- **Message Schema**: All events include `trace_id` for distributed tracing
- **Topics**: Hierarchical structure (`taylor/projects/created`, `taylor/plugins/installed`)

#### **2. Add-Only Extension Pattern**
- **Implementation**: Plugin registration system + adapter interfaces
- **Benefits**: Zero-risk feature additions, backward compatibility
- **Plugin Isolation**: Iframe sandboxing with controlled communication
- **Extension Points**: Routes, event handlers, UI components

#### **3. Dependency Injection Pattern (Backend)**
- **Implementation**: FastAPI's dependency system for database, MQTT, auth
- **Benefits**: Testability, loose coupling, resource management
- **Scopes**: Singleton for connections, request-scoped for transactions

#### **4. Context API Pattern (Frontend)**
- **Implementation**: React Context for auth state, notifications, plugins
- **Benefits**: Centralized state, prop drilling elimination
- **State Management**: Immutable updates with proper invalidation

#### **5. Repository Pattern**
- **Implementation**: Database abstraction layer with async connection pooling
- **Benefits**: Database independence, transaction management
- **Connection Strategy**: Persistent pool with health checks

### 🔄 Data Flow & Communication Patterns

#### **Authentication Flow**
```mermaid
sequenceDiagram
    participant FE as Frontend
    participant API as FastAPI
    participant KC as Keycloak
    participant DB as PostgreSQL

    FE->>API: Login Request
    API->>KC: OIDC Token Exchange
    KC-->>API: JWT + User Claims
    API->>DB: Store Session
    API-->>FE: Session Token + Expiry

    Note over FE,DB: Session Management
    FE->>API: API Request + Session Token
    API->>DB: Validate Session
    API-->>FE: Authorized Response
```

#### **Event Processing Flow**
```mermaid
sequenceDiagram
    participant SRC as Event Source
    participant MQTT as Message Bus
    participant SUB as Event Subscriber
    participant DB as PostgreSQL
    participant OTEL as OpenTelemetry

    SRC->>MQTT: Publish Event + Trace ID
    MQTT->>SUB: Route to Subscribers
    SUB->>OTEL: Create Span
    SUB->>DB: Mirror Event
    SUB->>OTEL: Complete Span

    Note over SRC,OTEL: End-to-End Traceability
```

#### **Plugin Communication Pattern**
```mermaid
sequenceDiagram
    participant Host as TaylorDash Host
    participant IF as Plugin Iframe
    participant API as Backend API

    Host->>IF: Load Plugin + Config
    IF->>Host: Register Capabilities
    IF->>Host: Request API Access
    Host->>API: Proxy Request + Auth
    API-->>Host: Response + Validation
    Host-->>IF: Filtered Response

    Note over Host,API: Sandboxed Execution
```

### ⚡ Performance Considerations

#### **Database Strategy**
- **Connection Pooling**: AsyncPG pool with configurable min/max connections
- **Query Optimization**: Indexed foreign keys, prepared statements
- **Transaction Management**: Explicit boundaries for consistency
- **Read Replicas**: Future scaling path for read-heavy workloads

#### **Caching Strategy**
- **Browser Caching**: Static assets with versioned URLs
- **API Caching**: Conditional requests with ETags
- **Session Caching**: Redis-ready session store design
- **Plugin Caching**: Iframe persistence across navigation

#### **Async Patterns**
- **Backend**: Full async/await with proper error boundaries
- **Frontend**: Concurrent API calls with Promise.allSettled
- **Event Processing**: Non-blocking MQTT handlers with DLQ
- **Resource Management**: Proper cleanup in finally blocks

### 🔒 Security Model & Architecture

#### **Authentication & Authorization**
- **OIDC Integration**: Keycloak for enterprise-grade identity management
- **Role-Based Access**: Admin, Maintainer, Viewer with granular permissions
- **Session Management**: Short-lived tokens with secure refresh patterns
- **API Security**: Bearer tokens + API key dual authentication

#### **Plugin Security Model**
- **Iframe Sandboxing**: Cross-origin isolation with controlled communication
- **Permission Model**: Explicit capability grants per plugin
- **API Proxying**: Backend validates all plugin API requests
- **Content Security**: Strict CSP headers for XSS prevention

#### **Network Security**
- **TLS Termination**: Traefik with HSTS and security headers
- **Internal Communication**: Encrypted service-to-service
- **Secrets Management**: Environment variables + Docker secrets
- **Local-First**: No external dependencies in production

### 📊 Observability Architecture

#### **OpenTelemetry Integration**
- **Tracing**: End-to-end request tracing with correlation IDs
- **Metrics**: Custom business metrics + system metrics
- **Logging**: Structured logging with trace correlation
- **Instrumentation**: Automatic + manual spans for key operations

#### **Monitoring Strategy**
- **Health Checks**: Deep health validation across all services
- **Alerting**: Prometheus rules for critical system states
- **Dashboards**: Grafana dashboards for operations visibility
- **Performance**: Response time tracking + SLA monitoring

### 🔧 Key Architectural Decisions

#### **Technology Stack Rationale**
- **FastAPI**: Async performance + automatic OpenAPI documentation
- **React**: Component reusability + extensive ecosystem
- **MQTT**: Lightweight pub/sub perfect for single-node deployment
- **PostgreSQL**: ACID compliance + JSON support for flexibility
- **Docker Compose**: Simple orchestration for local deployment

#### **Storage Architecture Decisions**
- **PostgreSQL for Metadata**: Normalized schema with referential integrity
- **VictoriaMetrics for Time-Series**: High compression + retention policies
- **MinIO for Artifacts**: Versioned storage with S3 compatibility
- **Separation of Concerns**: Right storage engine for each data type

#### **Security Architecture Decisions**
- **Keycloak over Custom Auth**: Enterprise-grade security out of the box
- **Plugin Isolation**: Safety over performance for extensibility
- **Local-First**: Reduced attack surface vs cloud dependencies
- **Defense in Depth**: Multiple security layers at each level

### Stack highlights

- **Frontend**: React, [Tailwind](https://tailwindcss.com/), React Router, [React Flow](https://reactflow.dev/) (node-based UIs).
- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (async), OTel instrumentation, Prom metrics.
- **Messaging**: [Mosquitto MQTT](https://mosquitto.org/) (lightweight, perfect for single-node).
- **Storage**: Postgres (metadata), [VictoriaMetrics](https://docs.victoriametrics.com/) (TSDB default), Timescale (SQL-forward option via hypertables).
- **Auth**: [Keycloak](https://www.keycloak.org/) OIDC + RBAC (admin/maintainer/viewer).
- **Edge**: [Traefik](https://doc.traefik.io/traefik/) TLS/HSTS middleware.
- **Observability**: [OpenTelemetry](https://opentelemetry.io/) + [Prometheus](https://prometheus.io/).
- **Orchestration**: [Docker Compose](https://docs.docker.com/compose/) (single host).

## 🧩 Features

- **Visual Project Canvas** ([React Flow](https://reactflow.dev/)) with component nodes, dependencies, and progress badges.
- **Multi-view UI** (tabs/perspectives) with role-aware tiles and hot-swap behavior.
- **HUD plugin system** with a Midnight HUD example (draggable/pinnable widgets, persisted layout).
- **Session memory**: MinIO versioned briefs + DB pointers; "Resume Brief" on login.
- **Event contracts**: JSON schemas on MQTT topics with `trace_id` for end-to-end tracing.
- **Observability**: `/metrics` (Prom text format) + OTel spans/attributes.
- **Security**: OIDC, short presigned URLs for downloads, strict headers at the edge.
- **Add-only evolution**: adapters and plugins—never mutate the frame.

## 🚀 Quickstart

**Prereqs**: Docker + Docker Compose, hosts entry (e.g., `tracker.local`), and your `.env` set.

```bash
# 1) Clone
git clone git@github.com:11bztaylor/TaylorDashv1.git
cd TaylorDashv1

# 2) Prerequisites check
docker compose version        # Verify command works
netstat -tulpn | grep :1883   # Check MQTT port free

# 3) Bring it up
docker compose up -d

# 4) Open
#   Frontend:   https://tracker.local
#   API docs:   https://tracker.local/api/docs
#   Keycloak:   https://tracker.local/kc
#   MinIO:      https://tracker.local/minio
```

### 5-Minute Setup Validation

```bash
# Quick health check
docker compose ps

# Full validation suite
bash ops/validate_p1.sh     # healthchecks, RBAC 401, metrics, MQTT echo, plugin route smoke

# Troubleshooting? See docs/infrastructure/quick-troubleshooting.md
```

## 🖥️ Midnight HUD Plugin (example)

A "floating cards" HUD with midnight/cyber glass theme, draggable/minimizable/pinnable, state persisted across navigation. Lives at `examples/midnight-hud/` and mounts in TaylorDash under **Plugins → Midnight HUD**. (Built with React + [Tailwind](https://tailwindcss.com/); React Router for persistence demo.)

**Run example (standalone):**

```bash
cd examples/midnight-hud
npm i
npm run dev
```

## 📚 Documentation (Diátaxis)

TaylorDash uses the [Diátaxis](https://diataxis.fr/) framework so you always know where to look and what to read:

- **Tutorials** – first-time, step-by-step ("your first visual plan", "HUD basics").
- **How-tos** – task recipes (runbooks, backup/restore, release ceremony).
- **Reference** – API, events, metrics, views schema.
- **Explanation** – architecture, storage choices, security model.

Docs are versioned (MkDocs + mike) so older releases remain browsable.

## 🔐 Security

- [Keycloak](https://www.keycloak.org/) OIDC for authN/authZ; roles: admin, maintainer, viewer.
- [Traefik](https://doc.traefik.io/traefik/) TLS/HSTS at the edge.
- **Secrets**: never commit tokens; use env files or Docker secrets.
- **Local-only** by default; no egress required after setup.
- See `SECURITY.md` for reporting and response.

## 📈 Observability

- [OpenTelemetry](https://opentelemetry.io/) in the backend (traces/logs/metrics).
- [Prometheus](https://prometheus.io/) scrapes `/metrics` (counters, gauges, histograms with labels).
- Grafana dashboards included (starter) for system health and event throughput.

## 🗃️ Storage Strategy

**Postgres**: normalized metadata + append-only events.

**TSDB**:
- Default [VictoriaMetrics](https://docs.victoriametrics.com/) (single binary, efficient retention/compression).
- Optional [TimescaleDB](https://docs.timescale.com/) for SQL-first workflows (hypertables).

**MinIO**: versioned artifacts (docs, briefs, exports) with versionId tracked in DB.

## 🧭 Conventions & Releases

- [Conventional Commits](https://conventionalcommits.org/) (required): `feat:`, `fix:`, `docs:`, `refactor:`, `perf:`, `test:`, `chore:`… (use `!` for breaking).
- [SemVer](https://semver.org/) releases: MAJOR = breaking, MINOR = features, PATCH = fixes.
- **Signed, annotated tags** → GitHub Releases → docs version bump (mike) → snapshot (Postgres/TSDB) → MinIO versionIds recorded.

## 🛠️ Tech You'll See Inside

- [FastAPI](https://fastapi.tiangolo.com/) (Python) for the API.
- React + [Tailwind](https://tailwindcss.com/) for the UI.
- [React Flow](https://reactflow.dev/) for the canvas.
- [Mosquitto](https://mosquitto.org/) (MQTT) for events.
- [Docker Compose](https://docs.docker.com/compose/) for orchestration.
- [Keycloak](https://www.keycloak.org/) for OIDC & RBAC.
- [Traefik](https://doc.traefik.io/traefik/) for TLS/HSTS.
- [OpenTelemetry](https://opentelemetry.io/) + [Prometheus](https://prometheus.io/) for observability.
- [VictoriaMetrics](https://docs.victoriametrics.com/) / [TimescaleDB](https://docs.timescale.com/) for time-series.
- MinIO for object storage.

## 🧪 Validate Phase-1 (one command)

```bash
bash ops/validate_p1.sh
# checks: service health, RBAC 401, /metrics exposed, MQTT pub/sub, plugin route smoke
```

## 🤝 Contributing

1. Open an issue with the provided templates (bug/feature).
2. Follow [Conventional Commits](https://conventionalcommits.org/); PRs use our template (docs + ADR when contracts change).
3. No direct pushes to main. Short-lived branches + required review.

## 📜 License

Apache-2.0 (see `LICENSE`).

## 🙌 Acknowledgements & References

- [Conventional Commits](https://conventionalcommits.org/) & [SemVer](https://semver.org/) for clean release hygiene.
- [Diátaxis](https://diataxis.fr/) documentation framework.
- [OpenTelemetry](https://opentelemetry.io/) & [Prometheus](https://prometheus.io/) for unifying traces, logs, metrics.
- [Mosquitto](https://mosquitto.org/) (MQTT) for lightweight pub/sub on a single node.
- [VictoriaMetrics](https://docs.victoriametrics.com/) and [Timescale Hypertables](https://docs.timescale.com/) for time-series power.
- [Keycloak](https://www.keycloak.org/) for OIDC + RBAC; [Traefik](https://doc.traefik.io/traefik/) for TLS/HSTS; [Docker Compose](https://docs.docker.com/compose/) for local orchestration.
- [React Flow](https://reactflow.dev/), [FastAPI](https://fastapi.tiangolo.com/), [Tailwind](https://tailwindcss.com/) for developer ergonomics and speed.

---

<p align="center">
  <strong>🌌 Build your visual mission control. Add-only. Event-driven. Beautiful.</strong>
</p>
