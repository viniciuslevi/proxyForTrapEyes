# 🚀 Início Rápido - TrapEyes

Guia rápido para colocar o TrapEyes funcionando em 5 minutos!

## ⚡ Instalação Rápida

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/trapeyes.git
cd trapeyes

# 2. Crie ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 3. Instale dependências
pip install -r requirements.txt

# 4. Inicie o servidor
python app.py
```

## 🌐 Acesse o Dashboard

Abra seu navegador: **http://localhost:8080**

## 📤 Teste Enviando Dados

### Opção 1: Script Automático

```bash
./test_detection.sh
```

### Opção 2: cURL Manual

```bash
curl -X POST http://localhost:8080/api/messages \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2025-11-20 15:30:45",
    "tempo_inferencia_ms": 87.5,
    "deteccoes": {
      "total": 15,
      "limiar_confianca": 0.5,
      "confianca_media": 0.9234,
      "ocupacao_pct": 18.5,
      "area_total_px": 12345.67,
      "itens": [
        {
          "classe_id": 0,
          "confianca": 0.9523,
          "bounding_box": [120, 250, 165, 295]
        }
      ]
    },
    "diagnostico": {
      "ocupacao_excessiva": false,
      "anormal": false
    },
    "lora_id": "LORA-001"
  }'
```

### Opção 3: Python

```python
import requests
import datetime

def enviar_teste():
    payload = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tempo_inferencia_ms": 87.5,
        "deteccoes": {
            "total": 15,
            "limiar_confianca": 0.5,
            "confianca_media": 0.9234,
            "ocupacao_pct": 18.5,
            "area_total_px": 12345.67,
            "itens": [
                {
                    "classe_id": 0,
                    "confianca": 0.9523,
                    "bounding_box": [120, 250, 165, 295]
                }
            ]
        },
        "diagnostico": {
            "ocupacao_excessiva": False,
            "anormal": False
        },
        "lora_id": "LORA-001"
    }

    response = requests.post(
        "http://localhost:8080/api/messages",
        json=payload
    )

    print(response.json())

enviar_teste()
```

## ✅ Verificar Status

```bash
# Health check
curl http://localhost:8080/health

# Estatísticas
curl http://localhost:8080/api/stats

# Listar detecções
curl http://localhost:8080/api/messages
```

## 🎯 Próximos Passos

1. ✅ Servidor funcionando
2. ✅ Teste enviado com sucesso
3. ✅ Dashboard acessível

**Agora integre com seu sistema IoT!**

Veja o [README.md](README.md) completo para:

- Integração com seu modelo de IA
- Configurações avançadas
- Deploy em produção
- API completa

## ❓ Problemas?

### Porta em uso

```bash
PORT=8081 python app.py
```

### Flask não encontrado

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Permissão negada no script

```bash
chmod +x test_detection.sh
```

---

**Pronto! Você está rodando o TrapEyes! 🦟✨**
