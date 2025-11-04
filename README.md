# 🚨 TrapEyes Message Server

Sistema de monitoramento em tempo real que recebe mensagens via HTTP POST e armazena em memória para visualização.

## ✨ Características

- 📡 **API REST** para receber mensagens
- 📊 **Dashboard Web** para visualizar mensagens em tempo real  
- 🐳 **Docker** pronto para uso
- ☁️ **Terraform** para deploy na AWS
- 💾 **Armazenamento em memória** (até 1000 mensagens)

## 🚀 Execução Rápida

### Com Docker (Recomendado)

```bash
# 1. Configure as variáveis (opcional)
cp .env.example .env

# 2. Execute
docker compose up -d

# 3. Acesse
open http://localhost:5000
```

### Sem Docker

```bash
# 1. Instale dependências
pip install -r requirements.txt

# 2. Execute
python app.py
```

## 📋 Endpoints da API

### POST /api/messages
Recebe mensagens de dispositivos IoT

**Exemplo:**
```bash
curl -X POST http://localhost:5000/api/messages \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Alerta de temperatura alta!",
    "device_id": "sensor-01",
    "location": "Sala 1",
    "temperature": 35.5,
    "alert_level": "high"
  }'
```

### GET /api/messages
Lista todas as mensagens

**Exemplo de resposta:**
```json
{
  "success": true,
  "messages": [
    {
      "message": "Alerta de temperatura alta!",
      "device_id": "sensor-01",
      "location": "Sala 1",
      "temperature": 35.5,
      "alert_level": "high",
      "timestamp": "2025-11-03T10:30:00.000000",
      "source_ip": "192.168.1.100"
    }
  ],
  "count": 1,
  "stats": {
    "total_messages": 1,
    "errors": 0
  }
}
```

### GET /api/stats
Retorna estatísticas do servidor

### GET /health
Health check para monitoramento

### GET /
Dashboard web interativo

## 🧪 Testando a Aplicação

```bash
# Enviar mensagem de teste
curl -X POST http://localhost:5000/api/messages \
  -H "Content-Type: application/json" \
  -d '{"message": "Teste", "device_id": "test-01"}'

# Verificar mensagens
curl http://localhost:5000/api/messages

# Ver estatísticas
curl http://localhost:5000/api/stats
```

## 📱 Exemplo de Integração com ESP32/Pico W

### Arduino/ESP32
```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

void enviarMensagem(float temperatura) {
  HTTPClient http;
  http.begin("http://seu-servidor:5000/api/messages");
  http.addHeader("Content-Type", "application/json");
  
  StaticJsonDocument<200> doc;
  doc["message"] = "Leitura do sensor";
  doc["device_id"] = "esp32-01";
  doc["location"] = "Sala 1";
  doc["temperature"] = temperatura;
  doc["alert_level"] = temperatura > 30 ? "high" : "low";
  
  String json;
  serializeJson(doc, json);
  
  int httpCode = http.POST(json);
  http.end();
}
```

### MicroPython/Pico W
```python
import urequests
import ujson

def enviar_mensagem(temperatura):
    url = "http://seu-servidor:5000/api/messages"
    dados = {
        "message": "Leitura do sensor",
        "device_id": "pico-01",
        "location": "Sala 1",
        "temperature": temperatura,
        "alert_level": "high" if temperatura > 30 else "low"
    }
    
    try:
        resposta = urequests.post(
            url,
            json=dados,
            headers={"Content-Type": "application/json"}
        )
        print(f"Status: {resposta.status_code}")
        resposta.close()
    except Exception as e:
        print(f"Erro: {e}")
```

## 🐳 Docker

### Build e execução
```bash
# Build
docker build -t trapeyes-server .

# Executar
docker run -d \
  -p 5000:5000 \
  -e PORT=5000 \
  -e MAX_MESSAGES=1000 \
  --name trapeyes \
  trapeyes-server

# Ver logs
docker logs -f trapeyes
```

### Docker Compose
```bash
# Iniciar
docker compose up -d

# Ver logs
docker compose logs -f

# Parar
docker compose down
```

## ☁️ Deploy na AWS

Veja o guia completo de deploy em [terraform/README.md](terraform/README.md)

Opções disponíveis:
- **AWS App Runner** (simples e gerenciado)
- **ECS Fargate** (completo com VPC, ALB, RDS)

## 🔧 Configuração

### Variáveis de Ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `PORT` | `5000` | Porta do servidor HTTP |
| `MAX_MESSAGES` | `1000` | Máximo de mensagens em memória |
| `DEBUG` | `false` | Modo debug do Flask |

## 📊 Dashboard

O dashboard web oferece:
- 📈 Visualização em tempo real das mensagens
- 📊 Estatísticas de uso
- 🔄 Atualização automática a cada 5 segundos
- 🎨 Interface responsiva e moderna
- 🔍 Detalhamento de cada mensagem com badges coloridos

Acesse em: http://localhost:5000

## 🛡️ Segurança

- ✅ Container executa como usuário não-root
- ✅ Imagem baseada em Python slim
- ✅ Health checks configurados
- ✅ Restart automático em caso de falha
- ⚠️ **Importante**: Configure HTTPS em produção

## 🆘 Solução de Problemas

### Erro ao iniciar
```bash
# Verificar logs
docker compose logs

# Verificar portas
netstat -tlnp | grep :5000
```

### Mensagens não aparecem
- Verifique se o JSON está válido
- Confirme que está enviando para o endpoint correto
- Verifique os logs: `docker compose logs -f`

## 📄 Estrutura do Projeto

```
proxy/
├── app.py                  # Aplicação Flask principal
├── requirements.txt        # Dependências Python
├── Dockerfile             # Imagem Docker
├── docker-compose.yml     # Orquestração
├── .env                   # Variáveis de ambiente
├── .env.example          # Exemplo de configuração
├── .gitignore            # Arquivos ignorados
├── README.md             # Esta documentação
└── terraform/            # Infraestrutura como código
    ├── simple.tf         # Deploy simples (App Runner)
    ├── main.tf           # Deploy completo (ECS)
    └── README.md         # Guia de deploy
```

---

**Desenvolvido com ❤️ para TrapEyes**
