# Estágio 1: Builder
FROM python:3.12-slim AS builder

# Instala o uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Estágio 2: Final
FROM python:3.12-slim

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY . .

# Garante que o ambiente virtual seja usado
ENV PATH="/app/.venv/bin:$PATH"

# Coleta arquivos estáticos
RUN python manage.py collectstatic --noinput

# Porta padrão do Django
EXPOSE 8000

# Executa com Gunicorn para produção
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
