# Using the Agents (Inputs, Outputs, and Prompts)

> The Orchestrator **must** call a specialist agent for each unit of work and never do the agent's job itself.

## Agent Roster & Responsibilities

| Agent | What it owns | Inputs | Outputs |
|---|---|---|---|
| **Project Manager** | Scoping, dependencies, acceptance criteria, ADR stubs | Current state (snapshot), backlog, failures | Session Plan (≤7 tasks), acceptance criteria, ADR draft refs |
| **Architecture/Contracts** | OpenAPI, event JSON schemas; breaking-change gate | ADRs, API/events deltas | Updated specs; schema diffs |
| **Infra/Compose** | docker-compose, health, restart, networks/volumes, Traefik TLS/HSTS | Infra ADRs, service list | Compose diffs, healthcheck scripts |
| **Backend (Async)** | FastAPI async, Keycloak JWT, MQTT pub/sub, DLQ, TSDB abstraction, MinIO presigns | API/events contracts, secrets | Service code, /health & /metrics hooks |
| **Frontend (Views/Tabs)** | React+TS, OIDC, multi-view tabs, React Flow canvas, plugin tiles | UI contracts | App shell, view persistence, tiles |
| **Observability** | OTel spans, metrics inventory, Grafana starter dashboards | /metrics candidates, trace points | Instrumentation code, Grafana JSON |
| **Security/RBAC** | Keycloak realm/roles, Traefik HSTS, Mosquitto auth/TLS, secret linting | Security ADRs | Realm export, conf snippets, checks |
| **Adapters** | HA ingest, Docker/UniFi stubs, strict async I/O | Integration contracts | Adapter stubs, tests |
| **QA/Tests** | pytest-asyncio, resilience tests, `validate_p1.sh` | Acceptance criteria | Test suites, reports |
| **Scribe/Docs** | MkDocs (Diátaxis), ADRs, Resume Brief, Run Journal | Diffs, PRs, traces | Updated docs/ADRs; brief in MinIO |

**Why this split:** It mirrors well-known multi-agent orchestration patterns (controller routes → specialists execute) and helps scale reliably.

---

## Interface Conventions

- **All task handoffs** include: `trace_id`, acceptance criteria, inputs/outputs, and checklists.  
- **Every agent** must update the **Run Journal** (JSONL) and emit OTel spans.  
- **Security first**: backend-only secrets; API guarded by Keycloak OIDC (JWT) and role matrix.  
- **Metrics naming**: Prometheus-style (counters/gauges/histograms) exposed at `/metrics`.

---

## Example Orchestrator Prompts to Agents

**Project Manager**
- _"Scope 'Add MQTT DLQ' into tasks with acceptance criteria and identify risk owners. Update ADR if contracts change."_

**Architecture/Contracts**
- _"Validate that `tracker/events/*` payloads include `trace_id`, `idempotency_key`. If schema changes, propose ADR diff."_

**Infra/Compose**
- _"Add Mosquitto TLS listener + password_file, keep restart policies and HEALTHCHECK. Provide config diff + test steps."_

**Backend (Async)**
- _"Implement DLQ consumer with exponential backoff; add `taylor_dlq_total` counter and latency histogram."_

**Observability**
- _"Instrument FastAPI with OTel; ensure route spans correlate to logs and metrics. Provide Grafana panel JSON."_

**Security/RBAC**
- _"Export Keycloak realm with roles admin/maintainer/viewer; document JWT claims and curl test recipe."_

---

## Quality Gates (Agent-side)

- **Docs updated** (Diátaxis + ADR).  
- **/metrics** exposes new metrics with correct types/labels; Prometheus scrape succeeds.  
- **Security** validated (Keycloak JWT, Mosquitto TLS/password).  
- **Run Journal** entry written with `trace_id` and outcome.