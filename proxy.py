#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 Proxy Telegram para Raspberry Pi Pico W
==========================================

Este proxy recebe requisições HTTP do Pico W e as encaminha
para a API do Telegram via HTTPS, eliminando a necessidade
de implementar TLS no microcontrolador.

Uso:
    export TELEGRAM_TOKEN="seu_bot_token_aqui"
    python3 proxy_telegram.py

Endpoint:
    POST /send
    {
      "chat_id": "123456789",
      "text": "Mensagem do Pico W"
    }
"""

from flask import Flask, request, jsonify
import requests
import os
import logging
from datetime import datetime

# Configuração de logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

app = Flask(__name__)

# Configurações
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    print("❌ ERRO: Defina TELEGRAM_TOKEN como variável de ambiente")
    print("Exemplo: export TELEGRAM_TOKEN='1234567890:AAEhBOweik6ad2qkQfdsionLK2jlsds'")
    exit(1)

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Estatísticas
stats = {
    "total_requests": 0,
    "successful_sends": 0,
    "failed_sends": 0,
    "start_time": datetime.now()
}

@app.route('/send', methods=['POST'])
def send_message():
    """
    Recebe mensagem do Pico W e envia para Telegram
    
    Esperado:
    {
      "chat_id": "123456789",
      "text": "Mensagem do Pico W"
    }
    """
    global stats
    stats["total_requests"] += 1
    
    # Log da requisição
    client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    logging.info(f"📨 Requisição de {client_ip}")
    
    try:
        # Validação do JSON
        data = request.get_json()
        if not data:
            logging.warning("❌ JSON inválido ou ausente")
            return jsonify({"error": "JSON inválido ou ausente"}), 400
        
        if 'chat_id' not in data or 'text' not in data:
            logging.warning(f"❌ Parâmetros obrigatórios ausentes: {data}")
            return jsonify({"error": "Parâmetros 'chat_id' e 'text' são obrigatórios"}), 400
        
        chat_id = str(data['chat_id'])
        text = str(data['text'])
        
        # Log da mensagem
        logging.info(f"💬 Para: {chat_id}")
        logging.info(f"📝 Texto: {text[:50]}{'...' if len(text) > 50 else ''}")
        
        # Payload para Telegram
        telegram_payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"  # Permite formatação HTML
        }
        
        # Envia para Telegram via HTTPS
        response = requests.post(
            f"{BASE_URL}/sendMessage", 
            json=telegram_payload,
            timeout=10
        )
        
        response_data = response.json()
        
        if response.status_code == 200 and response_data.get('ok'):
            stats["successful_sends"] += 1
            logging.info(f"✅ Mensagem enviada com sucesso!")
            return jsonify({
                "success": True, 
                "telegram_response": response_data,
                "message": "Mensagem enviada com sucesso"
            }), 200
        else:
            stats["failed_sends"] += 1
            logging.error(f"❌ Erro do Telegram: {response_data}")
            return jsonify({
                "success": False,
                "error": "Erro do Telegram",
                "telegram_response": response_data
            }), response.status_code
            
    except requests.exceptions.Timeout:
        stats["failed_sends"] += 1
        logging.error("⏱️ Timeout na requisição para Telegram")
        return jsonify({"error": "Timeout ao contatar Telegram"}), 408
        
    except requests.exceptions.RequestException as e:
        stats["failed_sends"] += 1
        logging.error(f"🌐 Erro de rede: {e}")
        return jsonify({"error": f"Erro de rede: {str(e)}"}), 500
        
    except Exception as e:
        stats["failed_sends"] += 1
        logging.error(f"💥 Erro interno: {e}")
        return jsonify({"error": f"Erro interno: {str(e)}"}), 500


@app.route('/status', methods=['GET'])
def status():
    """Retorna estatísticas do proxy"""
    uptime = datetime.now() - stats["start_time"]
    
    return jsonify({
        "status": "running",
        "uptime_seconds": int(uptime.total_seconds()),
        "stats": stats,
        "telegram_configured": bool(TELEGRAM_TOKEN)
    })


@app.route('/test', methods=['POST'])
def test():
    """
    Endpoint de teste - não envia para Telegram
    """
    data = request.get_json()
    logging.info(f"🧪 Teste recebido: {data}")
    
    return jsonify({
        "received": data,
        "message": "Teste recebido com sucesso (não enviado para Telegram)"
    }), 200


@app.route('/')
def home():
    """Página inicial com informações"""
    uptime = datetime.now() - stats["start_time"]
    
    return f"""
    <h1>🤖 Proxy Telegram para Pico W</h1>
    <h2>Status: ✅ Ativo</h2>
    <h3>📊 Estatísticas:</h3>
    <ul>
        <li>⏱️ Uptime: {uptime}</li>
        <li>📨 Total requisições: {stats['total_requests']}</li>
        <li>✅ Enviadas: {stats['successful_sends']}</li>
        <li>❌ Falhas: {stats['failed_sends']}</li>
    </ul>
    
    <h3>📋 Endpoints:</h3>
    <ul>
        <li><code>POST /send</code> - Enviar mensagem</li>
        <li><code>GET /status</code> - Status JSON</li>
        <li><code>POST /test</code> - Teste sem envio</li>
    </ul>
    
    <h3>🧪 Teste manual:</h3>
    <pre>
curl -X POST http://localhost:5000/send \\
  -H "Content-Type: application/json" \\
  -d '{{"chat_id":"SEU_CHAT_ID","text":"Teste do proxy!"}}'
    </pre>
    """, 200


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint não encontrado"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Erro interno do servidor"}), 500


if __name__ == '__main__':
    print("\n" + "="*50)
    print("🤖 PROXY TELEGRAM PARA RASPBERRY PI PICO W")
    print("="*50)
    print(f"📱 Token: {'✅ Configurado' if TELEGRAM_TOKEN else '❌ Não configurado'}")
    print(f"🌐 Será executado em todas as interfaces (0.0.0.0)")
    print(f"📡 Porta: {os.getenv('PORT', 5000)}")
    print()
    print("📋 Para testar:")
    print("curl -X POST http://localhost:5000/send \\")
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"chat_id":"SEU_CHAT_ID","text":"Teste!"}\'')
    print()
    print("🚀 Iniciando servidor...")
    print("="*50)
    
    app.run(
        host='0.0.0.0', 
        port=int(os.getenv("PORT", 5000)),
        debug=os.getenv("DEBUG", "false").lower() == "true"
    )