# First, build the application in the `/app` directory.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev
ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Create a non-root user
RUN useradd -m -u 1000 app

# add installation of brew install wkhtmltopdf

# Set working directory in container
WORKDIR /app

# Copy the application from the builder
COPY --from=builder --chown=app:app /app /app

# Switch to non-root user
USER app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

# Expose the port the app runs on
EXPOSE 8000

# Add these lines to your Dockerfile
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python3-cffi \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Run the application
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"] 