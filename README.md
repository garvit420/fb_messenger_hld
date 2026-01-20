# FB Messenger Backend Implementation with Cassandra

[![CI Pipeline](https://github.com/YOUR_USERNAME/fb-messenger-backend/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/fb-messenger-backend/actions/workflows/ci.yml)
[![CD Pipeline](https://github.com/YOUR_USERNAME/fb-messenger-backend/actions/workflows/cd.yml/badge.svg)](https://github.com/YOUR_USERNAME/fb-messenger-backend/actions/workflows/cd.yml)

---

## Problem Background & Motivation

### Why CI/CD?

In modern software development, **manual processes are the enemy of reliability**. Without automated pipelines:

| Challenge | Impact |
|-----------|--------|
| Manual testing | Bugs slip into production, inconsistent test coverage |
| Manual deployments | "Works on my machine" syndrome, deployment anxiety |
| No security scanning | Vulnerabilities discovered in production (too late!) |
| Slow feedback loops | Developers wait hours/days to know if code is broken |

### What CI/CD Solves

**Continuous Integration (CI)** ensures every code change is:
- Automatically tested against 47+ unit tests
- Scanned for security vulnerabilities (SAST with CodeQL)
- Checked for vulnerable dependencies (SCA with pip-audit)
- Validated for code quality (linting with flake8/black)

**Continuous Deployment (CD)** ensures:
- Consistent, reproducible deployments to Kubernetes
- Zero-downtime rolling updates
- Automated smoke tests post-deployment
- Quick rollback capability if issues arise

### Business Value

| Metric | Without CI/CD | With CI/CD |
|--------|---------------|------------|
| Deployment frequency | Weekly/Monthly | Multiple times per day |
| Lead time for changes | Days/Weeks | Hours |
| Mean time to recovery | Hours/Days | Minutes |
| Change failure rate | 15-30% | <5% |

---

## Application Overview

### What is FB Messenger Backend?

A **real-time messaging API** built with modern Python technologies, designed to handle:
- User-to-user messaging
- Conversation management
- Message history retrieval with pagination

### Technology Stack

| Component | Technology | Why |
|-----------|------------|-----|
| **API Framework** | FastAPI | Async support, automatic OpenAPI docs, type hints |
| **Language** | Python 3.11 | Modern features, strong ecosystem |
| **Database** | SQLite/Cassandra | Development flexibility, production scalability |
| **Container** | Docker | Consistent environments, easy deployment |
| **Orchestration** | Kubernetes | Auto-scaling, self-healing, rolling updates |

### Why This App for CI/CD Demo?

This application is ideal for demonstrating CI/CD because:
1. **Real-world complexity** - Multiple API endpoints, database interactions, authentication
2. **Testable** - 47 unit tests covering business logic
3. **Containerizable** - Stateless design fits container paradigm
4. **Scalable** - Kubernetes deployment with multiple replicas

---

This repository contains the stub code for the Distributed Systems course assignment to implement a Facebook Messenger backend using Apache Cassandra as the distributed database.

## Architecture

The application follows a typical FastAPI structure:

- `app/`: Main application package
  - `api/`: API routes and endpoints
  - `controllers/`: Controller logic (stubs provided)
  - `models/`: Database models (stubs provided, to be implemented by students)
  - `schemas/`: Pydantic models for request/response validation
  - `db/`: Database connection utilities (Cassandra client)

## Requirements

- Docker and Docker Compose (for containerized development environment)
- Python 3.11+ (for local development)

## Quick Setup with Docker

This repository includes a Docker setup to simplify the development process. All you need to get started is:

1. Clone this repository
2. Make sure Docker and Docker Compose are installed on your system
3. Run the initialization script:
   ```
   ./init.sh
   ```

This will:
- Start both FastAPI application and Cassandra containers
- Initialize the Cassandra keyspace and tables
- Optionally generate test data for development
- Make the application available at http://localhost:8000

Access the API documentation at http://localhost:8000/docs

To stop the application:
```
docker-compose down
```

### Test Data

The setup script includes an option to generate test data for development purposes. This will create:

- 10 test users (with IDs 1-10)
- 15 conversations between random pairs of users
- Multiple messages in each conversation with realistic timestamps

You can use these IDs for testing your API implementations. If you need to regenerate the test data:

```
docker-compose exec app python scripts/generate_test_data.py
```

## Manual Setup (Alternative)

If you prefer not to use Docker, you can set up the environment manually:

1. Clone this repository
2. Install Cassandra locally and start it
3. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install dependencies:
   ```
   uv pip install -r requirements.txt
   ```
5. Run the setup script to initialize Cassandra:
   ```
   python scripts/setup_db.py
   ```
6. Start the application:
   ```
   uvicorn app.main:app --reload
   ```

## Cassandra Data Model

For this assignment, you will need to design and implement your own data model in Cassandra to support the required API functionality:

1. Sending messages between users
2. Retrieving conversations for a user, ordered by most recent activity
3. Retrieving messages in a conversation, ordered by timestamp
4. Retrieving messages before a specific timestamp

Your data model should consider:
- Efficient distribution of data across nodes
- Appropriate partition keys and clustering columns
- How to handle pagination efficiently
- How to optimize for the required query patterns

## Assignment Tasks

You need to implement:

1. Cassandra schema design - create tables to support the required queries
2. Message and Conversation models (`app/models/`) to interact with Cassandra
3. Controller methods in the stub classes (`app/controllers/`):
   - Send Message from one user to another (only the DB interaction parts here. No need to implement websocket etc needed to actually deliver message to other user)
   - Get Recent Conversations of a user (paginated)
   - Get Messages in a particular conversation (paginated)
   - Get Messages in a conversation prior to a specific timestamp (paginated)

## API Endpoints

### Messages

- `POST /api/messages/`: Send a message from one user to another
- `GET /api/messages/conversation/{conversation_id}`: Get all messages in a conversation
- `GET /api/messages/conversation/{conversation_id}/before`: Get messages before a timestamp

### Conversations

- `GET /api/conversations/user/{user_id}`: Get all conversations for a user
- `GET /api/conversations/{conversation_id}`: Get a specific conversation

## Evaluation Criteria

- Correct implementation of all required endpoints
- Proper error handling and edge cases
- Efficient Cassandra queries (avoid hotspots and ensure good distribution)
- Code quality and organization
- Proper implementation of pagination
- Performance considerations for distributed systems
- Adherence to Cassandra data modeling best practices

---

## CI/CD Pipeline

This project includes a production-grade CI/CD pipeline using GitHub Actions.

### Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CI PIPELINE (ci.yml)                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐                        │
│  │  Lint   │  │  SAST   │  │   SCA   │  │  Test   │                        │
│  │ flake8  │  │ CodeQL  │  │pip-audit│  │ pytest  │                        │
│  │  black  │  │         │  │         │  │         │                        │
│  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘                        │
│       │            │            │            │                              │
│       └────────────┴─────┬──────┴────────────┘                              │
│                          │                                                  │
│                          ▼                                                  │
│                   ┌─────────────┐                                           │
│                   │Docker Build │                                           │
│                   │  + Trivy    │                                           │
│                   └──────┬──────┘                                           │
│                          │                                                  │
│                          ▼                                                  │
│                   ┌─────────────┐                                           │
│                   │  Container  │                                           │
│                   │ Smoke Test  │                                           │
│                   └──────┬──────┘                                           │
│                          │                                                  │
│                          ▼                                                  │
│                   ┌─────────────┐                                           │
│                   │ Push to     │                                           │
│                   │ DockerHub   │                                           │
│                   └─────────────┘                                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CD PIPELINE (cd.yml)                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐     │
│  │Create kind  │──▶│   Deploy    │──▶│   Verify    │──▶│   Smoke     │     │
│  │  Cluster    │   │   to K8s    │   │  Rollout    │   │   Tests     │     │
│  └─────────────┘   └─────────────┘   └─────────────┘   └─────────────┘     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### CI Pipeline Stages

| Stage | Tool | Purpose |
|-------|------|---------|
| **Linting** | flake8, black | Enforce PEP8 coding standards and consistent formatting |
| **SAST** | CodeQL | Static Application Security Testing - detect OWASP Top 10 vulnerabilities |
| **SCA** | pip-audit | Software Composition Analysis - identify vulnerable dependencies |
| **Unit Tests** | pytest | Validate business logic with 47+ tests |
| **Docker Build** | docker/build-push-action | Build production container image |
| **Image Scan** | Trivy | Scan container for OS/library vulnerabilities |
| **Container Test** | curl | Verify container runs and responds |
| **Registry Push** | DockerHub | Publish trusted image after all gates pass |

### CD Pipeline Stages

| Stage | Tool | Purpose |
|-------|------|---------|
| **Create Cluster** | kind | Spin up Kubernetes test cluster in GitHub Actions |
| **Deploy** | kubectl apply | Apply Kubernetes manifests |
| **Verify Rollout** | kubectl rollout status | Confirm deployment success |
| **Smoke Test** | kubectl port-forward + curl | Validate runtime behavior |
| **Cleanup** | kind delete | Clean up test resources |

### Setting Up GitHub Secrets

To enable the CI/CD pipeline, configure these secrets in your GitHub repository:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add the following secrets:

| Secret | Description | How to Get |
|--------|-------------|------------|
| `DOCKERHUB_USERNAME` | Your DockerHub username | Your DockerHub account |
| `DOCKERHUB_TOKEN` | DockerHub access token | DockerHub → Account Settings → Security → New Access Token |

### Running the Pipeline

**Automatic Triggers:**
- Push to `main` branch → CI pipeline runs
- Pull request to `main` → CI pipeline runs (no Docker push)
- CI success on `main` → CD pipeline triggers

**Manual Triggers:**
1. Go to **Actions** tab in GitHub
2. Select the workflow (CI or CD)
3. Click **Run workflow**

### Local Development Commands

```bash
# Run linting
flake8 app/ tests/
black --check app/ tests/

# Run tests
pytest tests/ -v

# Build Docker image locally
docker build -t fb-messenger-backend:local .

# Run container locally
docker run -p 8000:8000 fb-messenger-backend:local
```

### Kubernetes Deployment

The `k8s/` directory contains production-ready manifests:

```bash
# Apply to your cluster
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Check status
kubectl get pods -l app=fb-messenger-backend
kubectl get services
```

### Security Features

- **Multi-stage Docker build** - Minimizes attack surface
- **Non-root container user** - Principle of least privilege
- **CodeQL SAST** - Detects code vulnerabilities
- **pip-audit SCA** - Catches vulnerable dependencies
- **Trivy scanning** - Container vulnerability detection
- **Pod security context** - Kubernetes security hardening

---

## Results & Observations

### Pipeline Execution Summary

When the CI/CD pipeline runs successfully, you will observe:

#### CI Pipeline Results

| Stage | Expected Outcome |
|-------|------------------|
| **Lint** | `flake8`: 0 errors, `black`: All files formatted |
| **SAST (CodeQL)** | Security scan results in GitHub Security tab |
| **SCA (pip-audit)** | No known vulnerabilities in dependencies |
| **Unit Tests** | 47/47 tests passed, coverage report generated |
| **Docker Build** | Image built and tagged with commit SHA |
| **Trivy Scan** | Container vulnerabilities reported (CRITICAL/HIGH) |
| **Container Test** | Health endpoint returns 200 OK |
| **Registry Push** | Image available at DockerHub |

#### CD Pipeline Results

| Stage | Expected Outcome |
|-------|------------------|
| **Cluster Creation** | kind cluster `fb-messenger-test` created |
| **Deployment** | 2/2 pods running and ready |
| **Rollout Verification** | `deployment "fb-messenger-backend" successfully rolled out` |
| **Smoke Test** | `/health` and `/docs` endpoints accessible |

### Key Observations

1. **Parallel Job Execution**: CI jobs (lint, sast, sca, test) run in parallel, reducing total pipeline time
2. **Fail-Fast Behavior**: If any quality gate fails, Docker build is skipped (saving resources)
3. **Security-First Approach**: Multiple layers of security scanning catch issues at different levels
4. **Immutable Artifacts**: Docker images tagged with commit SHA ensure traceability

### Sample Pipeline Output

```
CI Pipeline - Run #15
├── lint ✓ (45s)
├── sast ✓ (2m 30s)
├── sca ✓ (30s)
├── test ✓ (1m 15s)
├── docker ✓ (3m 20s)
└── container-test ✓ (45s)

Total time: ~4 minutes (parallel execution)
```

---

## Limitations & Improvements

### Current Limitations

| Limitation | Description | Impact |
|------------|-------------|--------|
| **Test Environment** | Uses `kind` (local K8s) instead of real cluster | Not representative of production latency/scaling |
| **No Staging Environment** | Deploys directly to test cluster | No pre-production validation |
| **SQLite in Dev** | Different DB than production (Cassandra) | Potential data layer issues not caught |
| **No Secrets Management** | Uses GitHub Secrets only | Not suitable for multi-env deployments |
| **Manual Rollback** | No automated rollback on failure | Requires manual intervention |

### Future Improvements

#### Short-term Enhancements

| Improvement | Tool/Approach | Benefit |
|-------------|---------------|---------|
| **Add Helm Charts** | Helm | Parameterized, reusable K8s deployments |
| **Integration Tests** | pytest + testcontainers | Test with real Cassandra |
| **Code Coverage Gate** | Codecov | Enforce minimum coverage (e.g., 80%) |
| **Semantic Versioning** | semantic-release | Automated version bumping |

#### Long-term Enhancements

| Improvement | Tool/Approach | Benefit |
|-------------|---------------|---------|
| **GitOps** | ArgoCD / Flux | Declarative, auditable deployments |
| **Multi-Environment** | Kustomize overlays | Dev → Staging → Production promotion |
| **Observability** | Prometheus + Grafana | Real-time monitoring & alerting |
| **Feature Flags** | LaunchDarkly / Unleash | Safe progressive rollouts |
| **Canary Deployments** | Istio / Flagger | Gradual traffic shifting |

### Scalability Considerations

```
Current Setup:
  - 2 replicas (fixed)
  - Manual scaling

Recommended Production Setup:
  - Horizontal Pod Autoscaler (HPA)
  - Cluster Autoscaler
  - Pod Disruption Budgets
  - Resource quotas per namespace
```

---

## Conclusion

### What Was Achieved

This project demonstrates a **production-grade CI/CD pipeline** for a FastAPI application with:

| Component | Implementation |
|-----------|----------------|
| **Continuous Integration** | 6-stage pipeline with quality gates |
| **Continuous Deployment** | Automated Kubernetes deployment |
| **Security Scanning** | SAST (CodeQL), SCA (pip-audit), Container (Trivy) |
| **Code Quality** | Linting (flake8), Formatting (black) |
| **Testing** | 47 unit tests with coverage reporting |
| **Container Security** | Multi-stage build, non-root user, health checks |

### Key Learnings

1. **Shift-Left Security**: Integrating security scanning in CI catches vulnerabilities before they reach production
2. **Infrastructure as Code**: Kubernetes manifests and GitHub Actions YAML enable reproducible deployments
3. **Quality Gates**: Failing fast on linting/testing saves time and prevents bad code from progressing
4. **Observability**: Health checks and probes are essential for Kubernetes self-healing

### Pipeline Value Proposition

```
Code Push → Automated Tests → Security Scans → Container Build → K8s Deploy
     │            │                │                │              │
     └────────────┴────────────────┴────────────────┴──────────────┘
                           Fully Automated (~5 minutes)
```

This pipeline ensures that **every code change** is:
- ✅ Tested for correctness
- ✅ Scanned for security issues
- ✅ Built into an immutable container
- ✅ Deployed to Kubernetes
- ✅ Verified with smoke tests

**The result**: Faster, safer, and more reliable software delivery. 