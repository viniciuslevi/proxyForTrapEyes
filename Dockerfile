# Use Python 3.11 slim para uma imagem mais leve
FROM python:3.11-slim

# Metadados do container
LABEL maintainer="Levi"
LABEL description="Proxy Telegram para Raspberry Pi Pico W"
LABEL version="1.0"

# Criar usuário não-root para segurança
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Definir diretório de trabalho
WORKDIR /app

# Copiar requirements primeiro para aproveitar cache do Docker
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY proxy.py .

# Alterar propriedade dos arquivos para o usuário não-root
RUN chown -R appuser:appuser /app

# Trocar para usuário não-root
USER appuser

# Expor porta da aplicação
EXPOSE 5000

# Variáveis de ambiente com valores padrão
ENV FLASK_APP=proxy.py
ENV FLASK_ENV=production
ENV PORT=5000
ENV PYTHONUNBUFFERED=1

# Health check para verificar se o serviço está rodando
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/status || exit 1

# Comando padrão para executar a aplicação
CMD ["python", "proxy.py"]