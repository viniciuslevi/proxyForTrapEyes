# 🚀 Guia de Deploy - TrapEyes

Guia completo para deploy do TrapEyes em produção.

## 📋 Opções de Deploy

1. [Docker](#-docker-recomendado)
2. [Docker Compose](#-docker-compose)
3. [Servidor Linux](#-servidor-linux)
4. [Cloud Providers](#️-cloud-providers)

---

## 🐳 Docker (Recomendado)

### Build da Imagem

```bash
docker build -t trapeyes:latest .
```

### Run

```bash
docker run -d \
  --name trapeyes \
  -p 8080:8080 \
  -e PORT=8080 \
  -e MAX_MESSAGES=1000 \
  -e DEBUG=false \
  --restart unless-stopped \
  trapeyes:latest
```

### Verificar

```bash
docker logs -f trapeyes
curl http://localhost:8080/health
```

### Parar/Remover

```bash
docker stop trapeyes
docker rm trapeyes
```

---

## 📦 Docker Compose

### Iniciar

```bash
docker-compose -f docker-compose-updated.yml up -d
```

### Ver Logs

```bash
docker-compose -f docker-compose-updated.yml logs -f
```

### Parar

```bash
docker-compose -f docker-compose-updated.yml down
```

### Configuração com .env

Crie um arquivo `.env`:

```bash
PORT=8080
MAX_MESSAGES=1000
DEBUG=false
OCUPACAO_EXCESSIVA_THRESHOLD=20
ANORMAL_OCUPACAO_THRESHOLD=30
ANORMAL_MOSCAS_THRESHOLD=50
```

---

## 🖥️ Servidor Linux

### Preparação

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python 3.9+
sudo apt install python3 python3-pip python3-venv -y

# Clonar repositório
git clone https://github.com/seu-usuario/trapeyes.git
cd trapeyes
```

### Instalação

```bash
# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Instalar Gunicorn para produção
pip install gunicorn
```

### Configurar como Serviço (systemd)

Crie `/etc/systemd/system/trapeyes.service`:

```ini
[Unit]
Description=TrapEyes - Sistema de Detecção de Moscas
After=network.target

[Service]
Type=simple
User=seu-usuario
WorkingDirectory=/caminho/para/trapeyes
Environment="PATH=/caminho/para/trapeyes/venv/bin"
ExecStart=/caminho/para/trapeyes/venv/bin/gunicorn \
          --workers 4 \
          --bind 0.0.0.0:8080 \
          --timeout 120 \
          --access-logfile /var/log/trapeyes/access.log \
          --error-logfile /var/log/trapeyes/error.log \
          app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Iniciar Serviço

```bash
# Criar diretório de logs
sudo mkdir -p /var/log/trapeyes
sudo chown seu-usuario:seu-usuario /var/log/trapeyes

# Habilitar e iniciar
sudo systemctl daemon-reload
sudo systemctl enable trapeyes
sudo systemctl start trapeyes

# Verificar status
sudo systemctl status trapeyes

# Ver logs
sudo journalctl -u trapeyes -f
```

### Nginx como Reverse Proxy

Crie `/etc/nginx/sites-available/trapeyes`:

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

Ativar:

```bash
sudo ln -s /etc/nginx/sites-available/trapeyes /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL com Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d seu-dominio.com
```

---

## ☁️ Cloud Providers

### AWS EC2

1. Lance uma instância EC2 (Ubuntu 20.04+)
2. Configure Security Group (porta 8080)
3. Siga os passos de [Servidor Linux](#️-servidor-linux)

### Google Cloud Run

```bash
# Build e push para Container Registry
gcloud builds submit --tag gcr.io/SEU-PROJETO/trapeyes

# Deploy
gcloud run deploy trapeyes \
  --image gcr.io/SEU-PROJETO/trapeyes \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080
```

### Azure Container Instances

```bash
# Login
az login

# Criar grupo de recursos
az group create --name trapeyes-rg --location eastus

# Criar container
az container create \
  --resource-group trapeyes-rg \
  --name trapeyes \
  --image seu-registry/trapeyes:latest \
  --dns-name-label trapeyes \
  --ports 8080
```

### Heroku

```bash
# Criar app
heroku create trapeyes-app

# Configurar variáveis
heroku config:set PORT=8080
heroku config:set MAX_MESSAGES=1000

# Deploy
git push heroku main
```

---

## 🔒 Segurança

### Recomendações

1. **Firewall**: Abra apenas portas necessárias
2. **HTTPS**: Use sempre SSL em produção
3. **Autenticação**: Adicione autenticação se necessário
4. **Rate Limiting**: Implemente limite de requisições
5. **Monitoramento**: Configure alertas

### Firewall (ufw)

```bash
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

---

## 📊 Monitoramento

### Logs

```bash
# Systemd
sudo journalctl -u trapeyes -f

# Docker
docker logs -f trapeyes

# Docker Compose
docker-compose logs -f
```

### Métricas

Health check endpoint:

```bash
curl http://seu-dominio.com/health
```

Status da API:

```bash
curl http://seu-dominio.com/api/stats
```

---

## 🔄 Atualização

### Docker

```bash
docker pull trapeyes:latest
docker stop trapeyes
docker rm trapeyes
docker run -d --name trapeyes -p 8080:8080 trapeyes:latest
```

### Servidor Linux

```bash
cd /caminho/para/trapeyes
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart trapeyes
```

---

## 🐛 Troubleshooting

### Porta em uso

```bash
# Ver quem está usando
sudo lsof -i :8080

# Matar processo
sudo kill -9 PID
```

### Permissões

```bash
# Logs
sudo chown -R seu-usuario:seu-usuario /var/log/trapeyes

# Aplicação
sudo chown -R seu-usuario:seu-usuario /caminho/para/trapeyes
```

### Memória

Se estiver com problemas de memória, reduza MAX_MESSAGES:

```bash
export MAX_MESSAGES=500
```

---

## 📝 Checklist de Produção

- [ ] SSL/HTTPS configurado
- [ ] Firewall configurado
- [ ] Logs funcionando
- [ ] Health check respondendo
- [ ] Backup configurado
- [ ] Monitoramento ativo
- [ ] Autenticação (se necessário)
- [ ] Rate limiting (se necessário)
- [ ] Domínio configurado
- [ ] Testes de carga realizados

---

**Deploy bem-sucedido! 🎉**

Precisa de ajuda? Abra uma [issue](https://github.com/seu-usuario/trapeyes/issues)!
