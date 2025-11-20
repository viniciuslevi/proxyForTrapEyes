#!/bin/bash
# Script para limpar todos os registros do TrapEyes

echo "======================================================"
echo "🗑️  TRAPEYES - LIMPAR REGISTROS"
echo "======================================================"
echo ""

# Configurações
PORT=${PORT:-5000}
HOST=${HOST:-localhost}
URL="http://${HOST}:${PORT}/api/messages"

echo "📡 Conectando em: $URL"
echo "🗑️  Apagando todas as mensagens..."
echo ""

# Fazer requisição DELETE
response=$(curl -s -w "\n%{http_code}" -X DELETE "$URL")
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

# Verificar resposta
if [ "$http_code" -eq 200 ]; then
    echo "✅ Sucesso! Todas as mensagens foram apagadas."
    echo ""
    echo "Resposta do servidor:"
    echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
else
    echo "❌ Erro: HTTP $http_code"
    echo ""
    echo "Resposta do servidor:"
    echo "$body"
    exit 1
fi

echo ""
echo "======================================================"
