# ==========================================================
# Etapa 1 - Builder
# ==========================================================

FROM python:3.11-slim AS builder

WORKDIR /app

# Pacotes necessários apenas para compilação
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

ARG REQUIREMENTS=basic
COPY requirements.${REQUIREMENTS} /tmp/requirements.txt

RUN pip install \
    --no-cache-dir \
    --prefix=/install \
    -r /tmp/requirements.txt


# ==========================================================
# Etapa 2 - Runtime
# ==========================================================

FROM python:3.11-slim

WORKDIR /app

# Bibliotecas Python instaladas na etapa builder
COPY --from=builder /install /usr/local

# Apenas bibliotecas necessárias em runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copia toda a aplicação
COPY app/ /app/

# Cria diretório temporário
RUN mkdir -p /tmp && chmod 1777 /tmp

# Permissões compatíveis com OpenShift / OKD
RUN chgrp -R 0 /app && \
    chmod -R g=u /app

USER 1001

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

