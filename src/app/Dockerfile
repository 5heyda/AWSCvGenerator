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

# Run the application
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000"] 