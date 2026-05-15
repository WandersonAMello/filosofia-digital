FROM python:3.12-slim

# Instala o uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Instala dependências do sistema para Pillow
RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia arquivos de dependência
COPY pyproject.toml uv.lock ./

# Instala as dependências no sistema do container (evita problemas de PATH com venv)
RUN uv pip install --system --no-cache -r pyproject.toml

# Copia o código
COPY . .

# Coleta arquivos estáticos (usando uma chave temporária para a build)
RUN SECRET_KEY=build-key python manage.py collectstatic --noinput

EXPOSE 8000

# Executa com Gunicorn para produção
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
