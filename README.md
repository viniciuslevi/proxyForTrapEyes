# 🦟 TrapEyes - Sistema de Detecção de Moscas com IA

Sistema profissional de monitoramento e análise de detecções de moscas usando Inteligência Artificial e dispositivos IoT LoRa.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Sumário

- [Características](#-características)
- [Requisitos](#-requisitos)
- [Instalação](#-instalação)
- [Configuração](#️-configuração)
- [Uso](#-uso)
- [API](#-api)
- [Formato de Dados](#-formato-de-dados)
- [Dashboard](#-dashboard)
- [Deploy](#-deploy)
- [Contribuindo](#-contribuindo)

## 🎯 Características

- ✅ **Dashboard Profissional** - Interface dark theme moderna e responsiva
- ✅ **Análise em Tempo Real** - Atualização automática a cada 5 segundos
- ✅ **Diagnóstico Automático** - Detecção de ocupação excessiva e situações anormais
- ✅ **Visualizações Avançadas** - 4 gráficos interativos com Chart.js
- ✅ **API REST Completa** - Endpoints documentados para integração
- ✅ **Suporte IoT LoRa** - Múltiplos dispositivos simultâneos
- ✅ **Armazenamento em Memória** - Até 1000 mensagens (configurável)

## 💻 Requisitos

- Python 3.9+
- pip
- Navegador moderno (Chrome, Firefox, Safari, Edge)

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/trapeyes.git
cd trapeyes
```

### 2. Crie um ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

## ⚙️ Configuração

### Variáveis de Ambiente

Copie o arquivo de exemplo e configure:

```bash
cp .env.example .env
```

Edite o arquivo `.env`:

```bash
# Porta do servidor
PORT=8080

# Máximo de mensagens em memória
MAX_MESSAGES=1000

# Modo debug
DEBUG=false

# Thresholds de diagnóstico
OCUPACAO_EXCESSIVA_THRESHOLD=20
ANORMAL_OCUPACAO_THRESHOLD=30
ANORMAL_MOSCAS_THRESHOLD=50
```

### Thresholds Explicados

- **OCUPACAO_EXCESSIVA_THRESHOLD**: Percentual de ocupação para gerar alerta amarelo (padrão: 20%)
- **ANORMAL_OCUPACAO_THRESHOLD**: Percentual de ocupação para situação anormal (padrão: 30%)
- **ANORMAL_MOSCAS_THRESHOLD**: Quantidade de moscas para situação anormal (padrão: 50)

## 🎮 Uso

### Iniciar o Servidor

```bash
# Com ambiente virtual ativado
python app.py

# Ou especificando a porta
PORT=8080 python app.py
```

O servidor estará disponível em: `http://localhost:8080`

### Acessar o Dashboard

Abra seu navegador e acesse:

```
http://localhost:8080
```

## 📡 API

### Endpoints Disponíveis

#### 1. Dashboard Web

```
GET /
Retorna: Interface HTML do dashboard
```

#### 2. Receber Detecção (Formato Compacto LoRa)

```http
POST /api/messages
Content-Type: application/json

{
  "dt": "20112025",
  "hr": "14:30:45",
  "ti": 87,
  "m": 15,
  "cm": 0.92,
  "cmin": 0.85,
  "cmax": 0.95,
  "op": 7.77,
  "dg": {
    "oe": false,
    "an": false
  },
  "id": "LORA-001"
}
```

**Resposta de Sucesso:**

```json
{
  "success": true,
  "message": "Detecção recebida: 15 moscas",
  "stored": true,
  "message_id": 42,
  "diagnostico": {
    "ocupacao_excessiva": false,
    "anormal": false
  },
  "format": "lora_compact"
}
```

#### 3. Listar Detecções

```http
GET /api/messages
```

**Resposta:**

```json
{
  "success": true,
  "messages": [...],
  "count": 42,
  "stats": {
    "total_messages": 42,
    "errors": 0
  }
}
```

#### 4. Estatísticas

```http
GET /api/stats
```

#### 5. Health Check

```http
GET /health

Resposta:
{
  "status": "healthy",
  "service": "trapeyes-server",
  "timestamp": "2025-11-20T15:30:45.123456"
}
```

## 📊 Formato de Dados

### 📡 Formato Compacto LoRa (RECOMENDADO)

**Este é o formato otimizado para transmissão LoRa com mensagens curtas:**

```json
{
  "dt": "20112025",
  "hr": "14:30:45",
  "ti": 87,
  "m": 15,
  "cm": 0.92,
  "cmin": 0.85,
  "cmax": 0.95,
  "op": 7.77,
  "dg": {
    "oe": false,
    "an": false
  },
  "id": "LORA-001"
}
```

### 🔑 Legenda dos Campos (Formato Compacto)

| Campo   | Tipo   | Descrição                       | Exemplo    |
| ------- | ------ | ------------------------------- | ---------- |
| `dt`    | string | Data no formato `ddmmyyyy`      | "20112025" |
| `hr`    | string | Hora no formato `HH:MM:SS`      | "14:30:45" |
| `ti`    | int    | Tempo de inferência em ms       | 87         |
| `m`     | int    | Total de moscas detectadas      | 15         |
| `cm`    | float  | Confiança média do modelo (0-1) | 0.92       |
| `cmin`  | float  | Menor confiança detectada (0-1) | 0.85       |
| `cmax`  | float  | Maior confiança detectada (0-1) | 0.95       |
| `op`    | float  | Ocupação percentual da área     | 7.77       |
| `dg.oe` | bool   | Ocupação excessiva (`op > 20`)  | false      |
| `dg.an` | bool   | Anormal (`op > 30` OU `m > 50`) | false      |
| `id`    | string | ID do dispositivo LoRa          | "LORA-001" |

### 📐 Cálculo do Diagnóstico

```python
diagnostico = {
    "oe": ocupacao_percentual > 20,     # ocupacao_excessiva
    "an": (ocupacao_percentual > 30 or mosca_count > 50)  # anormal
}
```

### 💡 Exemplo Completo de Integração (Python)

```python
from datetime import datetime
import json
import requests

# ====================================
# SEUS DADOS DE DETECÇÃO
# ====================================
mosca_count = 15
conf_media = 0.92
conf_min = 0.85
conf_max = 0.95
ocupacao_percentual = 7.77
infer_time_ms = 87
LORA_ID = "LORA-001"

# ====================================
# CALCULAR DIAGNÓSTICO
# ====================================
diagnostico = {
    "oe": ocupacao_percentual > 20,     # ocupacao_excessiva
    "an": (ocupacao_percentual > 30 or mosca_count > 50)  # anormal
}

# ====================================
# MONTAR PAYLOAD COMPACTO LORA
# ====================================
now = datetime.now()

payload_lora = {
    "dt": now.strftime("%d%m%Y"),   # data compacta ddmmyyyy
    "hr": now.strftime("%H:%M:%S"), # hora HH:MM:SS
    "ti": infer_time_ms,            # tempo de inferência (ms)
    "m": mosca_count,               # total moscas
    "cm": conf_media,               # confiança média
    "cmin": conf_min,               # menor confiança
    "cmax": conf_max,               # maior confiança
    "op": ocupacao_percentual,      # ocupação %
    "dg": diagnostico,              # diagnostico
    "id": LORA_ID                   # id do nó LoRa
}

# ====================================
# JSON COMPACTO (IDEAL PARA LORA)
# ====================================
msg = json.dumps(payload_lora, separators=(",", ":"))
print(f"[LoRa] Payload: {len(msg)} bytes")
print(msg)

# ====================================
# ENVIAR VIA HTTP
# ====================================
response = requests.post(
    "http://localhost:8080/api/messages",
    json=payload_lora,
    timeout=5
)

result = response.json()
print(f"✅ Sucesso: {result['success']}")
print(f"📊 Diagnóstico: {result['diagnostico']}")
print(f"📝 Formato: {result['format']}")  # "lora_compact"
```

### 📦 Formato Expandido (Compatibilidade Legado)

O sistema ainda aceita o formato expandido para compatibilidade:

```json
{
  "timestamp": "2025-11-20 14:30:45",
  "tempo_inferencia_ms": 87,
  "deteccoes": {
    "total": 15,
    "limiar_confianca": 0.5,
    "confianca_media": 0.92,
    "ocupacao_pct": 7.77,
    "area_total_px": 10000,
    "itens": []
  },
  "diagnostico": {
    "ocupacao_excessiva": false,
    "anormal": false
  },
  "lora_id": "LORA-001"
}
```

> **💡 Nota:** O formato compacto LoRa é automaticamente expandido internamente pelo servidor, mantendo toda a funcionalidade do dashboard.

### ✅ Validações

**Formato Compacto:**

- ✅ `dt`: String 8 dígitos ddmmyyyy
- ✅ `hr`: String HH:MM:SS
- ✅ `ti`: Inteiro >= 0 (ms)
- ✅ `m`: Inteiro >= 0 (moscas)
- ✅ `cm`, `cmin`, `cmax`: Float 0.0-1.0
- ✅ `op`: Float 0.0-100.0 (%)
- ✅ `dg.oe`, `dg.an`: Booleanos
- ✅ `id`: String não vazia

**Formato Expandido:**

- ✅ `timestamp`: String "YYYY-MM-DD HH:MM:SS"
- ✅ `tempo_inferencia_ms`: Número positivo
- ✅ `deteccoes.total`: Inteiro >= 0
- ✅ `deteccoes.confianca_media`: Float 0.0-1.0
- ✅ `deteccoes.ocupacao_pct`: Float 0.0-100.0
- ✅ `diagnostico`: Objeto com booleanos
- ✅ `lora_id`: String não vazia

## 📈 Dashboard

### Métricas Exibidas

**Principais (4 cards grandes):**

1. Total de Moscas Detectadas
2. Capturas Realizadas
3. Confiança Média do Modelo IA
4. Dispositivos LoRa Ativos

**Secundárias (4 cards menores):** 5. Ocupação Média (%) 6. Tempo Médio de Inferência (ms) 7. Ocupação Excessiva (contador) 8. Detecções Anormais (contador)

### Gráficos

1. **🦟 Moscas Detectadas por Hora** - Linha com histórico de 24h
2. **🎯 Confiança Média do Modelo** - Linha com precisão ao longo do tempo
3. **📊 Ocupação por Captura** - Barras com % de ocupação (últimas 10)
4. **⚡ Tempo de Inferência** - Linha com performance (últimas 10)

### Status dos Dispositivos

Lista com todos os dispositivos LoRa mostrando:

- ID e localização
- Total de moscas detectadas
- Número de capturas realizadas
- Confiança média

### Tabela de Detecções

Últimas 15 detecções com:

- Timestamp completo
- Dispositivo LoRa
- Quantidade de moscas (com status 🟢🟡🔴)
- Confiança média
- Limiar usado
- Número de bounding boxes e % de ocupação

## 🔧 Integração com seu Sistema IoT

### Exemplo Completo (Python + LoRa)

```python
import requests
import json
from datetime import datetime

def enviar_deteccao_lora(mosca_count, conf_media, conf_min, conf_max,
                         ocupacao_pct, infer_time_ms, lora_id):
    """
    Envia detecção para o TrapEyes usando formato compacto LoRa

    Args:
        mosca_count: Total de moscas detectadas
        conf_media: Confiança média (0-1)
        conf_min: Menor confiança (0-1)
        conf_max: Maior confiança (0-1)
        ocupacao_pct: % de ocupação da área
        infer_time_ms: Tempo de inferência em ms
        lora_id: ID do dispositivo LoRa

    Returns:
        dict: Resposta do servidor
    """
    now = datetime.now()

    # Calcular diagnóstico
    diagnostico = {
        "oe": ocupacao_pct > 20,  # ocupacao_excessiva
        "an": (ocupacao_pct > 30 or mosca_count > 50)  # anormal
    }

    # Payload compacto LoRa
    payload = {
        "dt": now.strftime("%d%m%Y"),   # ddmmyyyy
        "hr": now.strftime("%H:%M:%S"), # HH:MM:SS
        "ti": infer_time_ms,            # tempo inferência (ms)
        "m": mosca_count,               # total moscas
        "cm": conf_media,               # confiança média
        "cmin": conf_min,               # menor confiança
        "cmax": conf_max,               # maior confiança
        "op": ocupacao_pct,             # ocupação %
        "dg": diagnostico,              # diagnóstico
        "id": lora_id                   # id LoRa
    }

    # JSON compacto para LoRa (sem espaços)
    msg_compacta = json.dumps(payload, separators=(",", ":"))
    print(f"[LoRa] Tamanho: {len(msg_compacta)} bytes")

    # Enviar para o servidor
    response = requests.post(
        "http://localhost:8080/api/messages",
        json=payload,
        timeout=5
    )

    return response.json()

# ====================================
# EXEMPLO DE USO COM SEU MODELO YOLO
# ====================================

# Após rodar a inferência do seu modelo...
# results = model(frame)
# boxes = results[0].boxes

mosca_count = len(boxes)
confidences = boxes.conf.cpu().numpy()

# Estatísticas de confiança
conf_media = float(confidences.mean()) if mosca_count > 0 else 0.0
conf_min = float(confidences.min()) if mosca_count > 0 else 0.0
conf_max = float(confidences.max()) if mosca_count > 0 else 0.0

# Calcular ocupação (área das bounding boxes / área total)
area_boxes = sum([
    (box[2] - box[0]) * (box[3] - box[1])
    for box in boxes.xyxy.cpu().numpy()
])
area_total = frame.shape[0] * frame.shape[1]
ocupacao_pct = round((area_boxes / area_total) * 100, 2)

# Tempo de inferência (já calculado)
infer_time_ms = round((t_end - t_start) * 1000)

# Enviar para TrapEyes
resultado = enviar_deteccao_lora(
    mosca_count=mosca_count,
    conf_media=conf_media,
    conf_min=conf_min,
    conf_max=conf_max,
    ocupacao_pct=ocupacao_pct,
    infer_time_ms=infer_time_ms,
    lora_id="LORA-001"
)

print(f"✅ Sucesso: {resultado['success']}")
print(f"📊 Diagnóstico: {resultado['diagnostico']}")
print(f"📝 Formato: {resultado['format']}")  # "lora_compact"
```

### Teste Rápido

Use o script de teste incluído (formato compacto LoRa):

```bash
chmod +x test_detection.sh
./test_detection.sh
```

Ou envie manualmente com curl:

```bash
# Formato compacto LoRa (recomendado)
curl -X POST http://localhost:8080/api/messages \
  -H "Content-Type: application/json" \
  -d @exemplo_payload_lora.json

# Ou diretamente:
curl -X POST http://localhost:8080/api/messages \
  -H "Content-Type: application/json" \
  -d '{
    "dt": "20112025",
    "hr": "14:30:45",
    "ti": 87,
    "m": 15,
    "cm": 0.92,
    "cmin": 0.85,
    "cmax": 0.95,
    "op": 7.77,
    "dg": {"oe": false, "an": false},
    "id": "LORA-001"
  }'
```

## 🐳 Deploy

### Docker (Recomendado)

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["python", "app.py"]
```

```bash
# Build
docker build -t trapeyes .

# Run
docker run -p 8080:8080 -e PORT=8080 trapeyes
```

### Docker Compose

```yaml
version: "3.8"

services:
  trapeyes:
    build: .
    ports:
      - "8080:8080"
    environment:
      - PORT=8080
      - MAX_MESSAGES=1000
      - DEBUG=false
    restart: unless-stopped
```

```bash
docker-compose up -d
```

### Produção

Para produção, use um servidor WSGI como Gunicorn:

```bash
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:8080 app:app
```

## 🧪 Testes

```bash
# Enviar detecção de teste
./test_detection.sh

# Verificar health
curl http://localhost:8080/health

# Ver estatísticas
curl http://localhost:8080/api/stats
```

## 📝 Logs

O sistema gera logs informativos:

```
[NORMAL] Detecção recebida: 15 moscas do dispositivo LORA-001
[ALERTA] Detecção recebida: 23 moscas do dispositivo LORA-003
[ANORMAL] Detecção recebida: 58 moscas do dispositivo LORA-004
[STORAGE] Detecção armazenada (total: 42)
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👥 Autores

- Seu Nome - [@seu-github](https://github.com/seu-usuario)

## 🙏 Agradecimentos

- Chart.js pela biblioteca de gráficos
- Flask pela framework web
- Comunidade open source

## 📞 Suporte

- 📧 Email: seu-email@exemplo.com
- 🐛 Issues: [GitHub Issues](https://github.com/seu-usuario/trapeyes/issues)
- 💬 Discussões: [GitHub Discussions](https://github.com/seu-usuario/trapeyes/discussions)

---

**Desenvolvido com 💜 para controle inteligente de pragas agrícolas**
