# Use Python 3.11 slim para uma imagem mais leve
FROM python:3.11-slim

# Metadados do container
LABEL maintainer="Levi"
LABEL description="TrapEyes Message Server - API REST + Frontend"
LABEL version="3.0"

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
COPY app.py .

# Alterar propriedade dos arquivos para o usuário não-root
RUN chown -R appuser:appuser /app

# Trocar para usuário não-root
USER appuser

# Expor porta da aplicação
EXPOSE 5000

# Variáveis de ambiente com valores padrão
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

# Comando padrão para executar a aplicação
CMD ["python", "app.py"]