# 🤖 Proxy Telegram para Raspberry Pi Pico W (Docker)

Este proxy recebe requisições HTTP do Pico W e as encaminha para a API do Telegram via HTTPS, eliminando a necessidade de implementar TLS no microcontrolador.

## 🚀 Execução com Docker (Recomendado)

### Pré-requisitos
- Docker
- Docker Compose

### Configuração Rápida

1. **Clone ou baixe o projeto**
```bash
git clone <seu-repo>
cd proxy
```

2. **Configure o token do Telegram**
```bash
# Opção 1: Usar arquivo .env
cp .env.example .env
# Edite o arquivo .env com seu token real

# Opção 2: Definir variável de ambiente
export TELEGRAM_TOKEN="seu_token_real_aqui"
```

3. **Execute com Docker Compose**
```bash
# Build e execução em modo detached (background)
docker-compose up -d

# Para ver os logs
docker-compose logs -f

# Para parar
docker-compose down
```

### Comandos Docker Alternativos

**Build manual da imagem:**
```bash
docker build -t telegram-proxy .
```

**Execução manual do container:**
```bash
docker run -d \
  --name telegram-proxy \
  -p 5000:5000 \
  -e TELEGRAM_TOKEN="seu_token_aqui" \
  telegram-proxy
```

## 📋 Endpoints Disponíveis

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/` | GET | Página inicial com estatísticas |
| `/send` | POST | Enviar mensagem para Telegram |
| `/status` | GET | Status do servidor (JSON) |
| `/test` | POST | Teste sem enviar para Telegram |

## 🧪 Teste do Proxy

**Após executar o container:**

```bash
# Teste básico
curl -X POST http://localhost:5000/send \
  -H "Content-Type: application/json" \
  -d '{"chat_id":"SEU_CHAT_ID","text":"Teste do proxy Docker!"}'

# Verificar status
curl http://localhost:5000/status
```

## 🔧 Configuração Avançada

### Variáveis de Ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `TELEGRAM_TOKEN` | **obrigatório** | Token do bot Telegram |
| `PORT` | `5000` | Porta do servidor |
| `DEBUG` | `false` | Modo debug do Flask |

### Exemplo de Uso no Pico W

```python
import network
import urequests
import json

# Conectar WiFi...

# Enviar mensagem via proxy
def enviar_mensagem(chat_id, texto):
    url = "http://SEU_IP:5000/send"
    dados = {
        "chat_id": chat_id,
        "text": texto
    }
    
    try:
        resposta = urequests.post(url, 
                                json=dados, 
                                headers={'Content-Type': 'application/json'})
        print(f"Status: {resposta.status_code}")
        print(f"Resposta: {resposta.text}")
        resposta.close()
        return True
    except Exception as e:
        print(f"Erro: {e}")
        return False

# Uso
enviar_mensagem("123456789", "Olá do Pico W!")
```

## 🔍 Monitoramento

**Ver logs em tempo real:**
```bash
docker-compose logs -f telegram-proxy
```

**Verificar health check:**
```bash
docker ps
# STATUS mostrará "healthy" se tudo estiver OK
```

**Estatísticas do container:**
```bash
docker stats telegram-proxy
```

## 🛠️ Desenvolvimento

**Para desenvolver localmente:**

```bash
# Executar em modo desenvolvimento (com reload automático)
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

**Para debug:**

```bash
# Executar container interativo
docker run -it --rm \
  -p 5000:5000 \
  -e TELEGRAM_TOKEN="seu_token" \
  telegram-proxy bash
```

## 🛡️ Segurança

- ✅ Container executa como usuário não-root
- ✅ Imagem baseada em Python slim (menos vulnerabilidades)
- ✅ Health checks configurados
- ✅ Restart automático em caso de falha
- ⚠️ **Importante**: Use HTTPS em produção (configure nginx ou traefik)

## 🆘 Solução de Problemas

**Container não inicia:**
```bash
# Verificar logs
docker-compose logs telegram-proxy

# Verificar se a porta está disponível
netstat -tlnp | grep :5000
```

**Erro de token:**
- Verifique se o `TELEGRAM_TOKEN` está correto
- Obtenha um novo token em [@BotFather](https://t.me/botfather)

**Erro de conexão:**
- Verifique se o container está rodando: `docker ps`
- Teste a conectividade: `curl http://localhost:5000/status`

---

## 📞 Como Obter o Chat ID

Para enviar mensagens, você precisa do chat_id:

1. Inicie uma conversa com seu bot no Telegram
2. Envie qualquer mensagem
3. Acesse: `https://api.telegram.org/bot<SEU_TOKEN>/getUpdates`
4. Procure por `"chat":{"id":123456789}` na resposta

---

**🎉 Agora seu proxy está dockerizado e pronto para uso!**