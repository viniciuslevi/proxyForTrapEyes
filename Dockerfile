FROM python:3.9-slim

# Metadados
LABEL maintainer="seu-email@exemplo.com"
LABEL description="TrapEyes - Sistema de Detecção de Moscas com IA"

# Diretório de trabalho
WORKDIR /app

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Copiar requirements e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY app.py config.py ./
COPY exemplo_payload.json ./

# Criar usuário não-root
RUN useradd -m -u 1000 trapeyes && \
    chown -R trapeyes:trapeyes /app

USER trapeyes

# Expor porta
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8080/health', timeout=2)" || exit 1

# Comando de inicialização
CMD ["python", "app.py"]
