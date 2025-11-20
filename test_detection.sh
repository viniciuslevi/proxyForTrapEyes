#!/bin/bash

##############################################
# Script de Teste - TrapEyes LoRa
##############################################
# Envia payloads compactados simulando
# dispositivos LoRa reais no campo
##############################################

echo "[TEST] Iniciando testes do TrapEyes (Formato LoRa Compacto)..."
echo "=========================================="

# URL do servidor
SERVER_URL="${SERVER_URL:-http://localhost:8080}"
ENDPOINT="$SERVER_URL/api/messages"

echo "[INFO] Servidor: $ENDPOINT"
echo ""

# Função para enviar detecção
send_detection() {
    local lora_id=$1
    local moscas=$2
    local conf_media=$3
    local ocupacao=$4
    local anormal=$5
    
    # Calcular diagnóstico
    local ocupacao_excessiva="false"
    local anormal_flag="false"
    
    if (( $(echo "$ocupacao > 20" | bc -l) )); then
        ocupacao_excessiva="true"
    fi
    
    if (( $(echo "$ocupacao > 30" | bc -l) )) || [ "$moscas" -gt 50 ]; then
        anormal_flag="true"
    fi
    
    # Data e hora atuais
    DATA=$(date +"%d%m%Y")
    HORA=$(date +"%H:%M:%S")
    
    # Tempo de inferência simulado (80-130ms)
    TEMPO_INFERENCIA=$((80 + RANDOM % 50))
    
    # Confiança mínima e máxima (simuladas)
    CONF_MIN=$(echo "$conf_media - 0.08" | bc)
    CONF_MAX=$(echo "$conf_media + 0.05" | bc)
    
    # Payload compacto LoRa
    PAYLOAD=$(cat <<EOF
{
  "dt": "$DATA",
  "hr": "$HORA",
  "ti": $TEMPO_INFERENCIA,
  "m": $moscas,
  "cm": $conf_media,
  "cmin": $CONF_MIN,
  "cmax": $CONF_MAX,
  "op": $ocupacao,
  "dg": {
    "oe": $ocupacao_excessiva,
    "an": $anormal_flag
  },
  "id": "$lora_id"
}
EOF
)
    
    echo "[SEND] Enviando: $lora_id - $moscas moscas (${ocupacao}% ocupacao)"
    
    # Enviar POST
    RESPONSE=$(curl -s -X POST "$ENDPOINT" \
        -H "Content-Type: application/json" \
        -d "$PAYLOAD" \
        -w "\n%{http_code}")
    
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | head -n-1)
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo "[OK] Sucesso! Resposta: $BODY"
    else
        echo "[ERROR] Erro HTTP $HTTP_CODE: $BODY"
    fi
    
    echo ""
}

##############################################
# CENARIOS DE TESTE
##############################################

echo "[TEST] Cenario 1: Deteccao Normal"
echo "------------------------------------------"
send_detection "LORA-001" 8 0.93 5.2 false
sleep 1

echo "[TEST] Cenario 2: Ocupacao Moderada"
echo "------------------------------------------"
send_detection "LORA-002" 18 0.89 15.5 false
sleep 1

echo "[TEST] Cenario 3: Ocupacao Excessiva (ALERTA > 20%)"
echo "------------------------------------------"
send_detection "LORA-003" 35 0.87 24.8 false
sleep 1

echo "[TEST] Cenario 4: Deteccao Anormal (CRITICO > 50 moscas)"
echo "------------------------------------------"
send_detection "LORA-004" 58 0.91 32.1 true
sleep 1

echo "[TEST] Cenario 5: Alta Confianca, Baixa Ocupacao"
echo "------------------------------------------"
send_detection "LORA-005" 3 0.97 1.8 false
sleep 1

echo "[TEST] Cenario 6: Multiplas deteccoes simultaneas"
echo "------------------------------------------"
send_detection "LORA-001" 12 0.88 8.3 false &
send_detection "LORA-002" 7 0.94 4.1 false &
send_detection "LORA-003" 21 0.86 14.2 false &
wait
sleep 1

echo "[TEST] Cenario 7: Infestacao Severa (CRITICO anormal)"
echo "------------------------------------------"
send_detection "LORA-006" 73 0.85 41.5 true
sleep 1

echo ""
echo "=========================================="
echo "[OK] Testes concluidos!"
echo ""
echo "[INFO] Acesse o dashboard em:"
echo "   $SERVER_URL"
echo ""
echo "[INFO] Para ver mensagens recebidas:"
echo "   curl $SERVER_URL/api/messages"
echo ""
echo "[INFO] Para ver estatisticas:"
echo "   curl $SERVER_URL/api/stats"
echo "=========================================="
