# =============================================================================
# Production-Ready Dockerfile for FB Messenger Backend
# =============================================================================
# This Dockerfile implements security best practices:
# 1. Multi-stage build - Reduces final image size and attack surface
# 2. Non-root user - Principle of least privilege
# 3. Health check - Container orchestration health monitoring
# 4. Minimal base image - Reduces vulnerabilities
# =============================================================================

# -----------------------------------------------------------------------------
# STAGE 1: Builder Stage
# Purpose: Install dependencies and compile any native extensions
# WHY: Separates build-time dependencies from runtime, reducing image size
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
# WHY: Some Python packages require gcc/g++ for native extensions
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc g++ && \
    pip install --no-cache-dir uv==0.1.* && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .

# Install dependencies to a virtual environment
# WHY: Isolates dependencies and makes copying to runtime stage cleaner
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN uv pip install --python /opt/venv/bin/python -r requirements.txt

# -----------------------------------------------------------------------------
# STAGE 2: Runtime Stage
# Purpose: Minimal production image with only runtime dependencies
# WHY: Smaller image = faster pulls, smaller attack surface, less CVEs
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS runtime

# Labels for image metadata
LABEL maintainer="FB Messenger Backend Team"
LABEL version="1.0.0"
LABEL description="Production-ready FB Messenger Backend API"

WORKDIR /app

# Create non-root user for security
# WHY: Running as root is a security risk - if container is compromised,
# attacker has root access. Non-root limits the blast radius.
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

# Copy virtual environment from builder stage
# WHY: Only copies the installed packages, not build tools
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY --chown=appuser:appgroup . .

# Switch to non-root user
USER appuser

# Expose the application port
EXPOSE 8000

# Health check for container orchestration
# WHY: Allows Docker/Kubernetes to monitor container health
# If /health fails, container can be restarted automatically
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the application in production mode
# WHY: Removed --reload flag (dev feature that watches for file changes)
# Production should use static code for performance and security
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
