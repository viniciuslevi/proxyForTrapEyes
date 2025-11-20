# 🦟 TrapEyes - Sistema de Detecção de Moscas com IA

Sistema profissional de monitoramento e análise de detecções de moscas usando Inteligência Artificial e dispositivos IoT LoRa.

![Dashboard](https://img.shields.io/badge/Dashboard-Profissional-blue)
![Python](https://img.shields.io/badge/Python-3.9+-green)
![Flask](https://img.shields.io/badge/Flask-3.0-red)
![Chart.js](https://img.shields.io/badge/Chart.js-4.4-orange)

## 🎯 Características

- **Dashboard Profissional**: Interface dark theme moderna e responsiva
- **Visualizações em Tempo Real**: 4 gráficos interativos com Chart.js
- **Análise de IA**: Processamento de detecções com confiança e bounding boxes
- **IoT LoRa**: Suporte para múltiplos dispositivos LoRa
- **API REST**: Endpoints para receber e consultar detecções
- **Atualização Automática**: Dashboard atualiza a cada 5 segundos

## 📊 Visualizações

1. **Detecções por Hora**: Gráfico de linha mostrando moscas detectadas ao longo do tempo
2. **Distribuição de Confiança**: Monitoramento da precisão do modelo de IA
3. **Moscas por Captura**: Gráfico de barras com últimas 10 capturas
4. **Atividade por Dispositivo LoRa**: Comparação de capturas entre sensores

## 🚀 Como Usar

### Iniciar o Servidor

```bash
cd /Users/H_CINTRA/Desktop/mosca/proxyForTrapEyes
source venv/bin/activate
PORT=8080 python app.py
```

### Acessar o Dashboard

Abra seu navegador em: **http://localhost:8080**

### Enviar Detecções

#### Usando cURL:

```bash
curl -X POST http://localhost:8080/api/messages \
  -H "Content-Type: application/json" \
  -d '{
    "data_captura": "2025-11-20",
    "hora_captura": "14:30:45",
    "quantidade_moscas": 15,
    "deteccoes_detalhadas": [
      {
        "classe_id": 0,
        "confianca": 0.9523,
        "bounding_box": [120, 250, 165, 295]
      },
      {
        "classe_id": 0,
        "confianca": 0.8834,
        "bounding_box": [340, 180, 385, 225]
      }
    ],
    "confianca_limite_usada": 0.5,
    "lora_id": "LORA-001"
  }'
```

#### Usando o Script de Teste:

```bash
./test_detection.sh
```

### Formato dos Dados

```python
payload = {
    "data_captura": "YYYY-MM-DD",           # Data da captura
    "hora_captura": "HH:MM:SS",             # Hora da captura
    "quantidade_moscas": int,                # Quantidade total detectada
    "deteccoes_detalhadas": [                # Lista de detecções
        {
            "classe_id": 0,                  # ID da classe (mosca)
            "confianca": float,              # Confiança (0.0 a 1.0)
            "bounding_box": [xmin, ymin, xmax, ymax]  # Coordenadas
        }
    ],
    "confianca_limite_usada": float,        # Threshold usado
    "lora_id": "LORA-XXX"                   # ID do dispositivo LoRa
}
```

## 📡 Endpoints API

### Receber Detecção

```
POST /api/messages
Content-Type: application/json
Body: {payload de detecção}
```

### Listar Detecções

```
GET /api/messages
Response: {
  "success": true,
  "messages": [...],
  "count": int,
  "stats": {...}
}
```

### Estatísticas

```
GET /api/stats
Response: {estatísticas do sistema}
```

### Health Check

```
GET /health
Response: {"status": "healthy", ...}
```

## 🎨 Dashboard Features

### Métricas Principais

- **Total de Moscas Detectadas**: Soma de todas as detecções
- **Capturas Realizadas**: Número total de imagens processadas
- **Confiança Média**: Precisão média do modelo de IA
- **Dispositivos LoRa**: Sensores ativos no sistema

### Gráficos Interativos

- Hover para ver detalhes
- Animações suaves nas transições
- Cores codificadas por severidade
- Atualização em tempo real

### Status dos Dispositivos

- Lista com todos os sensores LoRa
- Métricas individuais por dispositivo
- Indicadores de status (online/warning/erro)
- Localização de cada sensor

### Tabela de Detecções

- 15 detecções mais recentes
- Data/hora de cada captura
- Dispositivo LoRa responsável
- Quantidade de moscas
- Confiança média
- Threshold utilizado
- Número de bounding boxes

## 🔧 Tecnologias

- **Backend**: Flask 3.0 (Python)
- **Frontend**: HTML5, CSS3, JavaScript
- **Gráficos**: Chart.js 4.4
- **Fonte**: Inter (Google Fonts)
- **API**: REST JSON
- **Storage**: In-memory (até 1000 mensagens)

## 📈 Estatísticas Calculadas

- Total de moscas: Soma de `quantidade_moscas`
- Confiança média: Média de todas as `confianca` dos bounding boxes
- Capturas por dispositivo: Agrupamento por `lora_id`
- Detecções por hora: Agrupamento temporal
- Taxa de detecção: Moscas/captura

## 🎯 Casos de Uso

1. **Monitoramento Agrícola**: Controle de pragas em plantações
2. **Pesquisa Científica**: Estudos de comportamento de insetos
3. **Saúde Pública**: Monitoramento de vetores de doenças
4. **Indústria Alimentícia**: Controle de qualidade sanitária

## 🔒 Configurações

Variáveis de ambiente disponíveis:

```bash
PORT=8080                    # Porta do servidor
MAX_MESSAGES=1000           # Máximo de mensagens em memória
DEBUG=false                 # Modo debug
```

## 📝 Logs

O sistema gera logs informativos:

```
🦟 Detecção recebida: 15 moscas do dispositivo LORA-001
💾 Detecção armazenada (total: 42)
```

## 🚨 Alertas

O sistema classifica automaticamente as detecções:

- **🟢 Normal**: 0-10 moscas
- **🟡 Médio**: 11-20 moscas
- **🔴 Crítico**: 21+ moscas

## 📱 Dispositivos Simulados

O sistema inclui 5 dispositivos LoRa pré-configurados:

1. **LORA-001**: Sensor Campo A (Área Norte)
2. **LORA-002**: Sensor Campo B (Área Sul)
3. **LORA-003**: Sensor Estufa 1 (Estufa Principal)
4. **LORA-004**: Sensor Depósito (Armazenamento)
5. **LORA-005**: Sensor Portão (Entrada)

## 🔄 Atualizações em Tempo Real

- Dashboard: a cada 5 segundos
- Simulação de dados: a cada 10 segundos
- Gráficos: transições suaves sem reload

## 💡 Dicas

1. Use o script `test_detection.sh` para testes rápidos
2. Monitore os logs para debug
3. Configure o `MAX_MESSAGES` conforme necessário
4. Use diferentes `lora_id` para múltiplos sensores

## 🤝 Integração

Para integrar com seu sistema de detecção:

```python
import requests
import datetime

def enviar_deteccao(lista_deteccoes, mosca_count, lora_id, conf_threshold=0.5):
    now = datetime.datetime.now()

    payload = {
        "data_captura": now.strftime("%Y-%m-%d"),
        "hora_captura": now.strftime("%H:%M:%S"),
        "quantidade_moscas": mosca_count,
        "deteccoes_detalhadas": lista_deteccoes,
        "confianca_limite_usada": conf_threshold,
        "lora_id": lora_id
    }

    response = requests.post(
        "http://localhost:8080/api/messages",
        json=payload
    )

    return response.json()
```

## 📦 Dependências

```
Flask==3.0.0
flask-cors==4.0.0
Werkzeug==3.0.1
```

## 🎓 Documentação

Para mais informações sobre o formato dos dados e bounding boxes, consulte a documentação do seu modelo de detecção de objetos (YOLO, SSD, etc.).

---

**Desenvolvido com 💜 para controle inteligente de pragas**
