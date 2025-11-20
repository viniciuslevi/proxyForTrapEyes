# 📁 Estrutura do Projeto TrapEyes

```
trapeyes/
│
├── 📄 app.py                      # Aplicação Flask principal
├── 📄 config.py                   # Configurações e variáveis de ambiente
├── 📄 requirements.txt            # Dependências Python
│
├── 📚 Documentação
│   ├── README.md                  # Documentação principal
│   ├── QUICKSTART.md              # Início rápido (5 min)
│   ├── DEPLOY.md                  # Guia completo de deploy
│   ├── CONTRIBUTING.md            # Guia para contribuidores
│   └── PROJECT_STRUCTURE.md       # Este arquivo
│
├── 🐳 Docker
│   ├── Dockerfile                 # Imagem Docker
│   ├── docker-compose.yml         # Compose original
│   └── docker-compose-updated.yml # Compose com variáveis
│
├── 📋 Exemplos
│   ├── exemplo_payload.json       # Exemplo de payload completo
│   └── test_detection.sh          # Script de teste rápido
│
├── ⚙️ Configuração
│   ├── .env.example               # Template de variáveis de ambiente
│   ├── .gitignore                 # Arquivos ignorados pelo Git
│   └── LICENSE                    # Licença MIT
│
└── 🗄️ Terraform (opcional)
    └── terraform/
        ├── main.tf                # Infraestrutura como código
        └── README.md              # Instruções Terraform
```

## 📝 Descrição dos Arquivos

### Core

- **app.py**: Servidor Flask completo com API REST e dashboard web
- **config.py**: Gerenciamento de configurações via variáveis de ambiente
- **requirements.txt**: Flask 3.0, flask-cors, Werkzeug

### Documentação

- **README.md**: Documentação completa (instalação, uso, API, integração)
- **QUICKSTART.md**: Para começar em 5 minutos
- **DEPLOY.md**: Guias de deploy (Docker, Linux, Cloud)
- **CONTRIBUTING.md**: Como contribuir com o projeto

### Docker

- **Dockerfile**: Imagem otimizada com Python 3.9-slim
- **docker-compose-updated.yml**: Orquestração com health checks

### Exemplos

- **exemplo_payload.json**: Payload completo para testes
- **test_detection.sh**: Script bash para enviar detecção de teste

### Configuração

- **.env.example**: Template de variáveis (copiar para .env)
- **.gitignore**: Ignora venv/, *.pyc, .env, logs
- **LICENSE**: MIT License

## 🚀 Fluxo de Uso

1. **Instalação**: `pip install -r requirements.txt`
2. **Configuração**: Copiar `.env.example` para `.env`
3. **Execução**: `python app.py`
4. **Acesso**: `http://localhost:8080`
5. **Teste**: `./test_detection.sh`

## 📊 Endpoints da API

- `GET /` - Dashboard web
- `POST /api/messages` - Receber detecção
- `GET /api/messages` - Listar detecções
- `GET /api/stats` - Estatísticas
- `GET /health` - Health check

## 🎯 Arquivos Essenciais para o Git

```bash
# Incluir
- *.py
- *.md
- requirements.txt
- Dockerfile
- docker-compose*.yml
- exemplo_payload.json
- test_detection.sh
- .gitignore
- LICENSE

# Não incluir (ver .gitignore)
- venv/
- __pycache__/
- *.pyc
- .env (apenas .env.example)
- *.log
- .DS_Store
```

## 📦 Tamanho Estimado

- Código fonte: ~50KB
- Documentação: ~100KB
- Dependências (venv): ~50MB
- Imagem Docker: ~180MB

## 🔄 Atualização

Para atualizar o projeto:

```bash
git pull origin main
pip install -r requirements.txt
sudo systemctl restart trapeyes  # se usando systemd
```

---

**Estrutura limpa e organizada para produção! ✨**
