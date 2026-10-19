# -------------------------------------------------------------------
# Stage 1: Build wheels in an isolated builder container
# -------------------------------------------------------------------
FROM python:3.12-alpine3.20 AS builder

WORKDIR /build

RUN apk add --no-cache gcc musl-dev linux-headers libffi-dev

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt

# -------------------------------------------------------------------
# Stage 2: Final hardened, minimal, non-root runtime container
# -------------------------------------------------------------------
FROM python:3.12-alpine3.20

# Create dedicated non-root system group and user
RUN addgroup -g 10001 -S reliefgroup && \
    adduser -u 10001 -S reliefapp -G reliefgroup -h /home/reliefapp -s /sbin/nologin

WORKDIR /app

# Install runtime wheels from builder stage
COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache-dir /wheels/* && \
    rm -rf /wheels && \
    # Hardening: Purge pip and setuptools from runtime to eliminate CVE exposure
    python -m pip uninstall -y pip setuptools && \
    apk update && apk upgrade --no-cache && \
    apk add --no-cache curl

# Copy application source tree
COPY app/ /app/

# Ensure secure file ownership and permissions
RUN chown -R reliefapp:reliefgroup /app /home/reliefapp && \
    chmod -R 550 /app && \
    chmod -R 770 /home/reliefapp

USER reliefapp:reliefgroup

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://127.0.0.1:8000/health || exit 1

# Production WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "2", "--threads", "4", "--access-logfile", "-", "app:app"]
