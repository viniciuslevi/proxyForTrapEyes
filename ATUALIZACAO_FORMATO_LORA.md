# ✅ Atualização: Formato Compacto LoRa Implementado

## 🎯 O que foi feito

O sistema TrapEyes foi **atualizado para suportar o formato compacto otimizado para transmissão LoRa**, mantendo compatibilidade com o formato expandido anterior.

## 📊 Novo Formato (Produção)

### Formato Compacto LoRa

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

**Tamanho:** ~150 bytes (compactado sem espaços)

### Campos

| Campo   | Descrição             | Exemplo    |
| ------- | --------------------- | ---------- |
| `dt`    | Data ddmmyyyy         | "20112025" |
| `hr`    | Hora HH:MM:SS         | "14:30:45" |
| `ti`    | Tempo inferência (ms) | 87         |
| `m`     | Total moscas          | 15         |
| `cm`    | Confiança média       | 0.92       |
| `cmin`  | Menor confiança       | 0.85       |
| `cmax`  | Maior confiança       | 0.95       |
| `op`    | Ocupação (%)          | 7.77       |
| `dg.oe` | Ocupação excessiva    | false      |
| `dg.an` | Anormal               | false      |
| `id`    | ID dispositivo        | "LORA-001" |

## 🔧 Arquivos Atualizados

### 1. `app.py` (Servidor)

**Adicionado:**

- ✅ Função `expand_lora_payload()` para converter formato compacto → expandido
- ✅ Detecção automática do formato (compacto vs expandido)
- ✅ Suporte a ambos os formatos simultaneamente
- ✅ Campo `format` na resposta ("lora_compact" ou "expanded")
- ✅ Campo `original_format` nos dados armazenados

**Como funciona:**

```python
# Servidor detecta automaticamente o formato
if "dt" in payload:
    # Formato compacto LoRa - expandir internamente
    data = expand_lora_payload(payload)
else:
    # Formato expandido - usar direto
    data = payload
```

### 2. `README.md` (Documentação)

**Atualizado:**

- ✅ Formato compacto LoRa como formato **RECOMENDADO**
- ✅ Tabela de mapeamento de campos
- ✅ Exemplo completo de integração em Python
- ✅ Endpoint POST com novo formato
- ✅ Exemplos de teste com curl
- ✅ Seção de validações

### 3. `test_detection.sh` (Script de Teste)

**Reescrito completamente:**

- ✅ Usa formato compacto LoRa em todos os testes
- ✅ Gera data/hora automática no formato correto
- ✅ Calcula `cmin` e `cmax` simulados
- ✅ 7 cenários de teste diferentes
- ✅ Suporte a testes paralelos
- ✅ Logs detalhados

**Uso:**

```bash
chmod +x test_detection.sh
./test_detection.sh
```

### 4. `exemplo_payload_lora.json` (NOVO)

**Criado:**

- ✅ Exemplo completo do formato compacto
- ✅ Pronto para uso com curl
- ✅ Comentado e documentado

**Uso:**

```bash
curl -X POST http://localhost:8080/api/messages \
  -H "Content-Type: application/json" \
  -d @exemplo_payload_lora.json
```

### 5. `FORMATO_LORA.md` (NOVO)

**Criado:**

- ✅ Documentação técnica completa
- ✅ Comparação formato compacto vs expandido
- ✅ Tabela de mapeamento campo a campo
- ✅ Exemplo passo a passo de implementação
- ✅ Informações sobre limites LoRa (SF7-SF12)
- ✅ Tamanhos de payload por Spreading Factor
- ✅ Recomendações técnicas

### 6. `PROJETO_PRONTO.md`

**Atualizado:**

- ✅ Formato compacto como padrão
- ✅ Exemplo de integração atualizado
- ✅ Cálculo de diagnóstico explicado

### 7. `ATUALIZACAO_FORMATO_LORA.md` (Este arquivo)

**Criado:**

- ✅ Resumo de todas as mudanças
- ✅ Guia de migração
- ✅ Exemplos práticos

## 🚀 Como Usar (Integração)

### 1. Código Python (após inferência YOLO)

```python
from datetime import datetime
import json
import requests

# ====================================
# APÓS INFERÊNCIA
# ====================================
# results = model(frame)
# boxes = results[0].boxes

mosca_count = len(boxes)
confidences = boxes.conf.cpu().numpy()

# Estatísticas
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

# Tempo de inferência
infer_time_ms = round((t_end - t_start) * 1000)

# ====================================
# DIAGNÓSTICO
# ====================================
diagnostico = {
    "oe": ocupacao_percentual > 20,  # ocupacao_excessiva
    "an": (ocupacao_percentual > 30 or mosca_count > 50)  # anormal
}

# ====================================
# PAYLOAD COMPACTO LORA
# ====================================
now = datetime.now()
LORA_ID = "LORA-001"

payload_lora = {
    "dt": now.strftime("%d%m%Y"),
    "hr": now.strftime("%H:%M:%S"),
    "ti": infer_time_ms,
    "m": mosca_count,
    "cm": conf_media,
    "cmin": conf_min,
    "cmax": conf_max,
    "op": ocupacao_percentual,
    "dg": diagnostico,
    "id": LORA_ID
}

# ====================================
# ENVIAR VIA HTTP (OU LORA)
# ====================================
# JSON compacto (sem espaços)
msg = json.dumps(payload_lora, separators=(",", ":"))
print(f"[LoRa] Tamanho: {len(msg)} bytes")

# Via HTTP
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

### 2. Teste Rápido

```bash
# Testar o servidor
./test_detection.sh

# Ou manualmente
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

## ✅ Vantagens

1. **Tamanho Reduzido**: ~50% menor (150 bytes vs 300+ bytes)
2. **Adequado para LoRa**: Funciona com SF7-SF8 sem problemas
3. **Nomes Curtos**: Chaves com 1-4 caracteres
4. **Compatibilidade**: Suporta ambos os formatos
5. **Novos Campos**: `cmin` e `cmax` para análise estatística
6. **Auto-detecção**: Servidor detecta formato automaticamente

## 🔄 Compatibilidade

### Formato Antigo (ainda funciona!)

```json
{
  "timestamp": "2025-11-20 14:30:45",
  "tempo_inferencia_ms": 87,
  "deteccoes": {
    "total": 15,
    "confianca_media": 0.92,
    "ocupacao_pct": 7.77,
    ...
  },
  "diagnostico": {
    "ocupacao_excessiva": false,
    "anormal": false
  },
  "lora_id": "LORA-001"
}
```

**O servidor aceita ambos!** Não há necessidade de migração imediata.

## 📏 Limites LoRa

| Spreading Factor | Payload Máx | Status             |
| ---------------- | ----------- | ------------------ |
| SF7              | 222 bytes   | ✅ **Recomendado** |
| SF8              | 222 bytes   | ✅ OK              |
| SF9              | 115 bytes   | ⚠️ Limite justo    |
| SF10+            | 51 bytes    | ❌ Muito pequeno   |

**Nosso payload:** ~150 bytes → **Funciona perfeitamente com SF7-SF8!**

## 🧪 Testes Realizados

✅ Servidor detecta formato compacto automaticamente
✅ Conversão para formato interno funciona corretamente
✅ Dashboard exibe dados convertidos normalmente
✅ Compatibilidade com formato expandido mantida
✅ Script de teste com 7 cenários diferentes
✅ Validação de campos obrigatórios

## 📖 Documentação

Para mais detalhes, consulte:

- **FORMATO_LORA.md**: Documentação técnica completa
- **README.md**: Guia geral do projeto
- **exemplo_payload_lora.json**: Exemplo prático
- **test_detection.sh**: Script de teste

## 🎯 Próximos Passos

1. ✅ Integrar com seu código de detecção
2. ✅ Testar localmente com `test_detection.sh`
3. ✅ Configurar gateway LoRa
4. ✅ Deploy em produção
5. ✅ Monitorar via dashboard

## 📞 Suporte

Se tiver dúvidas:

1. Leia **FORMATO_LORA.md**
2. Execute `./test_detection.sh`
3. Teste com `exemplo_payload_lora.json`
4. Consulte **README.md**

---

**✅ Sistema 100% pronto para produção com LoRa!**

**Desenvolvido com 💜 para transmissão eficiente via LoRa**
