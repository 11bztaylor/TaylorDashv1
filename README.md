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

## 🏗️ Architecture (Phase-1)

```mermaid
flowchart LR
  subgraph Client
    A[React + Tailwind App]
    V[Views/Tabs + React Flow]
    H[Midnight HUD Plugin]
  end

  subgraph Edge
    T[Traefik<br/>TLS+HSTS]
  end

  subgraph Core
    B[FastAPI Async Backend<br/>/health /metrics /api]
    K[Keycloak OIDC<br/>RBAC]
    Q[MQTT Broker<br/>(Mosquitto)]
    P[("Postgres")]
    S[("TSDB: VictoriaMetrics or Timescale")]
    M[("MinIO<br/>versioned objects")]
    PR[Prometheus]
  end

  A -->|OIDC| K
  A --> T --> B
  V --> A
  H --> A
  B <--> Q
  B <--> P
  B <--> S
  B <--> M
  PR --> B
```

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

# 2) Bring it up
docker compose up -d

# 3) Open
#   Frontend:   https://tracker.local
#   API docs:   https://tracker.local/api/docs
#   Keycloak:   https://tracker.local/kc
#   MinIO:      https://tracker.local/minio
```

### Validation

```bash
bash ops/validate_p1.sh     # healthchecks, RBAC 401, metrics, MQTT echo, plugin route smoke
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
