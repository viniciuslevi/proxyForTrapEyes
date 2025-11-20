# 📡 Formato Compacto LoRa - TrapEyes

## 🎯 Objetivo

Este documento detalha o **formato compacto otimizado para transmissão LoRa**, que reduz significativamente o tamanho das mensagens mantendo todas as informações essenciais.

## 📊 Comparação de Formatos

### Formato Compacto LoRa (ATUAL)

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

**Tamanho:** ~150 bytes (compactado, sem espaços)

### Formato Expandido (LEGADO)

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

**Tamanho:** ~300+ bytes

## 🔑 Mapeamento de Campos

| Compacto | Expandido                        | Tipo   | Descrição                  |
| -------- | -------------------------------- | ------ | -------------------------- |
| `dt`     | `timestamp` (data)               | string | Data ddmmyyyy → yyyy-mm-dd |
| `hr`     | `timestamp` (hora)               | string | Hora HH:MM:SS              |
| `ti`     | `tempo_inferencia_ms`            | int    | Tempo de inferência (ms)   |
| `m`      | `deteccoes.total`                | int    | Total de moscas            |
| `cm`     | `deteccoes.confianca_media`      | float  | Confiança média            |
| `cmin`   | _(novo)_                         | float  | Menor confiança            |
| `cmax`   | _(novo)_                         | float  | Maior confiança            |
| `op`     | `deteccoes.ocupacao_pct`         | float  | Ocupação (%)               |
| `dg.oe`  | `diagnostico.ocupacao_excessiva` | bool   | Op. excessiva              |
| `dg.an`  | `diagnostico.anormal`            | bool   | Anormal                    |
| `id`     | `lora_id`                        | string | ID do dispositivo          |

## 💡 Exemplo de Implementação

### 1. Preparar Dados (após inferência YOLO)

```python
from datetime import datetime
import json

# ====================================
# DADOS DA SUA DETECÇÃO
# ====================================
# Após rodar: results = model(frame)

mosca_count = len(boxes)
confidences = boxes.conf.cpu().numpy()

# Estatísticas de confiança
conf_media = float(confidences.mean()) if mosca_count > 0 else 0.0
conf_min = float(confidences.min()) if mosca_count > 0 else 0.0
conf_max = float(confidences.max()) if mosca_count > 0 else 0.0

# Calcular ocupação
area_boxes = sum([
    (box[2] - box[0]) * (box[3] - box[1])
    for box in boxes.xyxy.cpu().numpy()
])
area_total = frame.shape[0] * frame.shape[1]
ocupacao_percentual = round((area_boxes / area_total) * 100, 2)

# Tempo de inferência (você já tem isso)
t_end = time.time()
infer_time_ms = round((t_end - t_start) * 1000)
```

### 2. Calcular Diagnóstico

```python
# ====================================
# DIAGNÓSTICO AUTOMÁTICO
# ====================================
diagnostico = {
    "oe": ocupacao_percentual > 20,  # ocupacao_excessiva
    "an": (ocupacao_percentual > 30 or mosca_count > 50)  # anormal
}
```

### 3. Montar Payload Compacto

```python
# ====================================
# PAYLOAD COMPACTO LORA
# ====================================
now = datetime.now()
LORA_ID = "LORA-001"  # ID do seu dispositivo

payload_lora = {
    "dt": now.strftime("%d%m%Y"),   # "20112025"
    "hr": now.strftime("%H:%M:%S"), # "14:30:45"
    "ti": infer_time_ms,            # 87
    "m": mosca_count,               # 15
    "cm": conf_media,               # 0.92
    "cmin": conf_min,               # 0.85
    "cmax": conf_max,               # 0.95
    "op": ocupacao_percentual,      # 7.77
    "dg": diagnostico,              # {"oe": false, "an": false}
    "id": LORA_ID                   # "LORA-001"
}
```

### 4. Compactar JSON (LoRa)

```python
# ====================================
# COMPACTAR PARA TRANSMISSÃO LORA
# ====================================
# Remover espaços e quebras de linha
msg = json.dumps(payload_lora, separators=(",", ":"))

print(f"[LoRa] Tamanho da mensagem: {len(msg)} bytes")
print(f"[LoRa] Payload: {msg}")

# Exemplo de saída:
# [LoRa] Tamanho da mensagem: 147 bytes
# [LoRa] Payload: {"dt":"20112025","hr":"14:30:45","ti":87,"m":15,...}
```

### 5. Enviar via LoRa

```python
# ====================================
# TRANSMITIR VIA LORA
# ====================================
# Usando sua biblioteca LoRa
lora.send_payload(msg)

print(f"✅ Payload enviado via LoRa!")
```

### 6. Recepção no Gateway (HTTP)

```python
# ====================================
# NO GATEWAY: ENVIAR PARA TRAPEYES
# ====================================
import requests

# O gateway LoRa recebe a mensagem e envia para o servidor via HTTP
response = requests.post(
    "http://seu-servidor.com:8080/api/messages",
    json=payload_lora,  # Já está no formato correto!
    timeout=5
)

result = response.json()
print(f"✅ Servidor respondeu: {result['success']}")
print(f"📊 Diagnóstico: {result['diagnostico']}")
print(f"📝 Formato reconhecido: {result['format']}")  # "lora_compact"
```

## 🔄 Conversão Automática no Servidor

O servidor TrapEyes **detecta automaticamente** o formato e converte internamente:

```python
# No servidor (app.py)
def expand_lora_payload(compact_data):
    """
    Converte payload compacto LoRa para formato expandido interno
    """
    if "dt" in compact_data and "hr" in compact_data:
        # Formato compacto detectado - expandir
        dt = compact_data.get("dt")  # "20112025"
        hr = compact_data.get("hr")  # "14:30:45"

        # Converter ddmmyyyy → yyyy-mm-dd
        day = dt[0:2]
        month = dt[2:4]
        year = dt[4:8]
        timestamp = f"{year}-{month}-{day} {hr}"

        # Expandir para formato interno
        expanded = {
            "timestamp": timestamp,
            "tempo_inferencia_ms": compact_data.get("ti"),
            "deteccoes": {
                "total": compact_data.get("m"),
                "confianca_media": compact_data.get("cm"),
                "confianca_min": compact_data.get("cmin"),
                "confianca_max": compact_data.get("cmax"),
                "ocupacao_pct": compact_data.get("op"),
                # ... outros campos
            },
            "diagnostico": {
                "ocupacao_excessiva": compact_data.get("dg", {}).get("oe"),
                "anormal": compact_data.get("dg", {}).get("an")
            },
            "lora_id": compact_data.get("id")
        }

        return expanded
    else:
        # Já está expandido - retornar como está
        return compact_data
```

## ✅ Vantagens do Formato Compacto

1. **Tamanho Reduzido**: ~50% menor que o formato expandido
2. **Adequado para LoRa**: Respeita limitações de banda estreita
3. **Nomes Curtos**: Chaves com 1-4 caracteres
4. **Mantém Informações**: Nenhum dado essencial perdido
5. **Compatibilidade**: Servidor aceita ambos os formatos
6. **Novos Campos**: `cmin` e `cmax` adicionados

## 🧪 Testes

### Teste Local

```bash
# Usar o script de teste
./test_detection.sh
```

### Teste Manual (curl)

```bash
# Enviar payload compacto
curl -X POST http://localhost:8080/api/messages \
  -H "Content-Type: application/json" \
  -d '{
    "dt":"20112025",
    "hr":"14:30:45",
    "ti":87,
    "m":15,
    "cm":0.92,
    "cmin":0.85,
    "cmax":0.95,
    "op":7.77,
    "dg":{"oe":false,"an":false},
    "id":"LORA-001"
  }'
```

### Resposta Esperada

```json
{
  "success": true,
  "message": "Detecção recebida: 15 moscas",
  "stored": true,
  "message_id": 0,
  "diagnostico": {
    "ocupacao_excessiva": false,
    "anormal": false
  },
  "format": "lora_compact"
}
```

## 📏 Limites e Restrições LoRa

### Spreading Factor (SF) e Tamanho Máximo

| SF   | Velocidade  | Payload Máx | Status     |
| ---- | ----------- | ----------- | ---------- |
| SF7  | Mais rápido | 222 bytes   | ✅ OK      |
| SF8  | Rápido      | 222 bytes   | ✅ OK      |
| SF9  | Médio       | 115 bytes   | ⚠️ Limite  |
| SF10 | Lento       | 51 bytes    | ❌ Pequeno |
| SF11 | Muito lento | 51 bytes    | ❌ Pequeno |
| SF12 | Mais lento  | 51 bytes    | ❌ Pequeno |

**Nosso payload:** ~150 bytes → Funciona bem com SF7-SF8!

### Recomendações

- ✅ Use SF7 ou SF8 quando possível (melhor taxa/tamanho)
- ✅ O payload compacto cabe confortavelmente
- ✅ Margem para expansão futura
- ⚠️ Se precisar SF9+, considere remover campos opcionais

## 📖 Documentação Adicional

- **README.md**: Documentação principal do projeto
- **exemplo_payload_lora.json**: Exemplo do payload compacto
- **test_detection.sh**: Script de teste automatizado
- **DEPLOY.md**: Guia de implantação

## 🤝 Suporte

Se tiver dúvidas sobre o formato compacto:

1. Consulte este documento
2. Veja exemplos em `test_detection.sh`
3. Teste com `exemplo_payload_lora.json`
4. Abra uma issue no GitHub

---

**Desenvolvido com 💜 para transmissão eficiente via LoRa**
