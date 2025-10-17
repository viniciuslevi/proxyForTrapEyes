# 🤖 Proxy Telegram + AWS IoT Bridge

Este projeto oferece duas funcionalidades principais:

1. **Proxy HTTP → Telegram**: Recebe requisições HTTP do Pico W e encaminha para a API do Telegram via HTTPS
2. **🌉 Ponte AWS IoT → Telegram**: Conecta ao AWS IoT Core via MQTT e encaminha mensagens para o Telegram

## 🚀 Execução com Docker (Recomendado)

### Pré-requisitos
- Docker
- Docker Compose
- Credenciais AWS IoT Core (já incluídas no projeto)

### Configuração Rápida

1. **Clone ou baixe o projeto**
```bash
git clone <seu-repo>
cd proxy
```

2. **Configure as variáveis de ambiente**
```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite com suas configurações reais
nano .env
```

**Variáveis importantes:**
- `TELEGRAM_TOKEN`: Token do seu bot Telegram (obrigatório)
- `DEFAULT_CHAT_ID`: Chat ID padrão para mensagens IoT (recomendado)
- `MQTT_TOPIC`: Tópico MQTT para ouvir (padrão: sensor/data)

3. **Execute ambos os serviços**
```bash
# Build e execução em modo detached (background)
docker-compose up -d

# Para ver os logs de ambos os serviços
docker-compose logs -f

# Para ver logs de um serviço específico
docker-compose logs -f telegram-proxy
docker-compose logs -f mqtt-telegram-bridge

# Para parar ambos
docker-compose down
```

### Comandos Docker Alternativos

**Build manual da imagem:**
```bash
docker build -t telegram-proxy .
```

**Execução manual do proxy HTTP:**
```bash
docker run -d \
  --name telegram-proxy \
  -p 5000:5000 \
  -e TELEGRAM_TOKEN="seu_token_aqui" \
  telegram-proxy
```

**Execução manual da ponte MQTT:**
```bash
docker run -d \
  --name mqtt-bridge \
  -e TELEGRAM_TOKEN="seu_token_aqui" \
  -e DEFAULT_CHAT_ID="123456789" \
  -v $(pwd)/c7ced95a27be9307d25c3a100eb3a6dbfb2e1cc76d892fb8d4600c8268cc2388-certificate.pem.crt:/app/c7ced95a27be9307d25c3a100eb3a6dbfb2e1cc76d892fb8d4600c8268cc2388-certificate.pem.crt:ro \
  -v $(pwd)/c7ced95a27be9307d25c3a100eb3a6dbfb2e1cc76d892fb8d4600c8268cc2388-private.pem.key:/app/c7ced95a27be9307d25c3a100eb3a6dbfb2e1cc76d892fb8d4600c8268cc2388-private.pem.key:ro \
  -v $(pwd)/AmazonRootCA1.pem:/app/AmazonRootCA1.pem:ro \
  telegram-proxy python mqtt_telegram_bridge.py
```

## 📋 Funcionalidades Disponíveis

### 🌐 Proxy HTTP (Porta 5000)

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/` | GET | Página inicial com estatísticas |
| `/send` | POST | Enviar mensagem para Telegram |
| `/status` | GET | Status do servidor (JSON) |
| `/test` | POST | Teste sem enviar para Telegram |

### 🌉 Ponte AWS IoT Core → Telegram

- **Conecta automaticamente** ao AWS IoT Core (`a25833zo7tzuak-ats.iot.us-east-1.amazonaws.com:8883`)
- **Escuta mensagens MQTT** no tópico configurado (padrão: `sensor/data`)
- **Envia para Telegram** com formatação automática
- **Suporte a SSL/TLS** com certificados AWS IoT

## 🧪 Testando os Serviços

### Teste do Proxy HTTP

```bash
# Teste básico
curl -X POST http://localhost:5000/send \
  -H "Content-Type: application/json" \
  -d '{"chat_id":"SEU_CHAT_ID","text":"Teste do proxy Docker!"}'

# Verificar status
curl http://localhost:5000/status
```

### Teste da Ponte MQTT

**Formato de mensagem MQTT esperado:**

```json
{
  "chat_id": "123456789",
  "message": "Temperatura crítica detectada!",
  "sensor": "temp01",
  "temperature": 45.2,
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**Ou formato simples (usa chat padrão):**

```json
{
  "message": "Alerta: Temperatura alta!",
  "value": 35.5
}
```

**Resultado no Telegram:**
```
🤖 AWS IoT → Telegram

📢 Temperatura crítica detectada!

🌡️ Temperatura: 45.2°C
📡 Sensor: temp01
🕐 Timestamp: 2024-01-01T12:00:00Z

📡 Tópico: sensor/data
🕐 Recebido: 14:30:25
```

## 🔧 Configuração Avançada

### Variáveis de Ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `TELEGRAM_TOKEN` | **obrigatório** | Token do bot Telegram |
| `DEFAULT_CHAT_ID` | - | Chat ID padrão para mensagens IoT |
| `AWS_IOT_ENDPOINT` | `a25833zo7tzuak-ats.iot.us-east-1.amazonaws.com` | Endpoint AWS IoT |
| `AWS_IOT_PORT` | `8883` | Porta AWS IoT |
| `MQTT_TOPIC` | `sensor/data` | Tópico MQTT para ouvir |
| `CLIENT_ID` | `telegram-bridge` | ID do cliente MQTT |
| `PORT` | `5000` | Porta do proxy HTTP |
| `DEBUG` | `false` | Modo debug do Flask |

### Exemplo de Uso no Pico W

#### Via HTTP (Proxy):
```python
import network
import urequests
import json

def enviar_http(chat_id, texto):
    url = "http://SEU_IP:5000/send"
    dados = {"chat_id": chat_id, "text": texto}
    
    try:
        resposta = urequests.post(url, json=dados, 
                                headers={'Content-Type': 'application/json'})
        print(f"Status: {resposta.status_code}")
        resposta.close()
        return True
    except Exception as e:
        print(f"Erro: {e}")
        return False
```

#### Via MQTT (AWS IoT):
```python
import json
from umqtt.simple import MQTTClient

def enviar_mqtt(temperatura, umidade):
    # Configurar cliente MQTT com certificados
    client = MQTTClient("pico-sensor", "a25833zo7tzuak-ats.iot.us-east-1.amazonaws.com", 
                       port=8883, ssl=True)
    
    # Dados do sensor
    dados = {
        "message": f"Leitura do sensor",
        "temperature": temperatura,
        "humidity": umidade,
        "sensor": "pico-dht22",
        "timestamp": "2024-01-01T12:00:00Z"
    }
    
    try:
        client.connect()
        client.publish("sensor/data", json.dumps(dados))
        client.disconnect()
        return True
    except Exception as e:
        print(f"Erro MQTT: {e}")
        return False
```

## � Monitoramento

**Ver logs em tempo real:**
```bash
# Todos os serviços
docker-compose logs -f

# Apenas proxy HTTP
docker-compose logs -f telegram-proxy

# Apenas ponte MQTT
docker-compose logs -f mqtt-telegram-bridge
```

**Verificar health check:**
```bash
docker ps
# STATUS mostrará "healthy" para serviços ativos
```

**Estatísticas dos containers:**
```bash
docker stats
```

## 🛡️ Segurança

- ✅ Container executa como usuário não-root
- ✅ Imagem baseada em Python slim (menos vulnerabilidades)
- ✅ Health checks configurados
- ✅ Restart automático em caso de falha
- ✅ Certificados AWS IoT montados como read-only
- ✅ Credenciais via variáveis de ambiente
- ⚠️ **Importante**: Use HTTPS em produção (configure nginx ou traefik)

## 🆘 Solução de Problemas

### Problemas Gerais

**Containers não iniciam:**
```bash
# Verificar logs
docker-compose logs

# Verificar se as portas estão disponíveis
netstat -tlnp | grep :5000
```

**Erro de token Telegram:**
- Verifique se o `TELEGRAM_TOKEN` está correto
- Obtenha um novo token em [@BotFather](https://t.me/botfather)

### Problemas MQTT/AWS IoT

**Erro de conexão MQTT:**
```bash
# Verificar logs específicos
docker-compose logs mqtt-telegram-bridge

# Verificar certificados
ls -la *.pem*
```

**Certificados inválidos:**
- Verifique se os arquivos `.pem.crt` e `.pem.key` existem
- Confirme se o endpoint AWS IoT está correto
- Teste conectividade: `telnet a25833zo7tzuak-ats.iot.us-east-1.amazonaws.com 8883`

**Mensagens não chegam:**
- Verifique se o `DEFAULT_CHAT_ID` está configurado
- Confirme se o tópico MQTT está correto
- Verifique se as mensagens estão no formato JSON válido

## 📞 Como Obter o Chat ID

Para enviar mensagens, você precisa do chat_id:

1. Inicie uma conversa com seu bot no Telegram
2. Envie qualquer mensagem
3. Acesse: `https://api.telegram.org/bot<SEU_TOKEN>/getUpdates`
4. Procure por `"chat":{"id":123456789}` na resposta

## 🏗️ Arquitetura do Sistema

```
[Dispositivos IoT] → [AWS IoT Core] → [MQTT Bridge] → [Telegram Bot API] → [Chat Telegram]
                                           ↑
[Pico W] → [HTTP Proxy] → [Telegram Bot API] → [Chat Telegram]
```

## 🚀 Fluxos Suportados

1. **HTTP → Telegram**: `Pico W` → `Proxy HTTP` → `Telegram`
2. **MQTT → Telegram**: `IoT Device` → `AWS IoT` → `MQTT Bridge` → `Telegram`
3. **Híbrido**: Ambos os fluxos funcionam simultaneamente

---

**🎉 Agora você tem uma ponte completa entre AWS IoT Core e Telegram!**