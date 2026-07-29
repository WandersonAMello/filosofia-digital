FROM python:3.13-slim

# Copia o binário do uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Dependências de sistema necessárias para Pillow e PostgreSQL
RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Cria usuário não-root por segurança
RUN addgroup --system appgroup && adduser --system --group appuser

# Copia e instala dependências
COPY pyproject.toml uv.lock ./
RUN uv pip install --system --no-cache -r pyproject.toml

# Copia o código da aplicação
COPY . .

# Ajusta permissões dos diretórios estáticos e mídia
RUN mkdir -p /app/staticfiles /app/media && \
    chown -R appuser:appgroup /app

# Coleta estáticos
RUN SECRET_KEY=build-key python manage.py collectstatic --noinput

USER appuser

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "config.wsgi:application"]
