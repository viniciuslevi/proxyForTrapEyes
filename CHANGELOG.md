# Changelog - TrapEyes

## [1.1.0] - 2025-11-20

### Adicionado

- Formato compacto LoRa implementado (~150 bytes)
- Auto-detecção de formato (compacto vs expandido)
- Campos `cmin` e `cmax` para análise de confiança
- Compatibilidade retroativa com formato expandido
- Função `expand_lora_payload()` para conversão automática

### Modificado

- Logs do servidor sem emoticons (formato [TAG] legível)
- Script de teste `test_detection.sh` com formato compacto
- Documentação atualizada com formato LoRa
- Banner de inicialização simplificado

### Formato de Dados

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

### Diagnóstico

```python
diag_curto = {
    "oe": diagnostico["ocupacao_excessiva"],  # op > 20
    "an": diagnostico["anormal"]              # op > 30 OU m > 50
}
```

### Compatibilidade

- SF7-SF8: Recomendado (222 bytes máximo)
- SF9: Funciona (115 bytes máximo)
- SF10+: Não recomendado (51 bytes máximo)

## [1.0.0] - 2025-11-20

### Inicial

- Servidor Flask com dashboard profissional
- API REST completa
- 4 gráficos interativos
- Suporte a múltiplos dispositivos LoRa
- Docker e Docker Compose
- Documentação completa
