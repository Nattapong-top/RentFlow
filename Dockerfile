FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:0.8.15 /uv /uvx /bin/

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH" \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

COPY application ./application
COPY custom_errors ./custom_errors
COPY domain ./domain
COPY infrastructure ./infrastructure
COPY presentation ./presentation

EXPOSE 8000

CMD ["uvicorn", "presentation.api.main:app", "--host", "0.0.0.0", "--port", "8000"]