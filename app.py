#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📱 TrapEyes Message Server
=========================

API REST para receber e visualizar mensagens de dispositivos IoT.
Envia notificações para o Telegram e armazena mensagens para visualização.

Endpoints:
    POST /api/messages - Recebe mensagens dos dispositivos
    GET /api/messages - Lista mensagens armazenadas
    GET / - Interface web para visualização
"""

import json
import logging
import os
from datetime import datetime
from typing import List, Dict
from collections import deque

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

# Configuração de logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurações do servidor
PORT = int(os.getenv("PORT", "5000"))
MAX_MESSAGES = int(os.getenv("MAX_MESSAGES", "1000"))  # Máximo de mensagens em memória

# Armazenamento em memória (pode ser substituído por banco de dados)
messages_storage: deque = deque(maxlen=MAX_MESSAGES)

# Estatísticas
stats = {
    "total_messages": 0,
    "errors": 0,
    "start_time": datetime.now()
}

app = Flask(__name__)
CORS(app)  # Permitir CORS para frontend

@app.route('/')
def index():
    """Página inicial com interface para visualizar mensagens"""
    html = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TrapEyes - Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 20px;
            text-align: center;
        }
        
        .header h1 {
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        
        .stat-card {
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        .stat-card h3 {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        
        .stat-card .value {
            color: #667eea;
            font-size: 2em;
            font-weight: bold;
        }
        
        .messages-container {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            max-height: 600px;
            overflow-y: auto;
        }
        
        .message-card {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            transition: transform 0.2s;
        }
        
        .message-card:hover {
            transform: translateX(5px);
        }
        
        .message-card.new {
            animation: slideIn 0.5s ease-out;
            border-left-color: #28a745;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(-20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        .message-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        
        .message-title {
            font-size: 1.2em;
            font-weight: bold;
            color: #333;
        }
        
        .message-time {
            color: #999;
            font-size: 0.9em;
        }
        
        .message-content {
            color: #666;
            line-height: 1.6;
        }
        
        .message-meta {
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #ddd;
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        
        .badge {
            background: #667eea;
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.85em;
        }
        
        .badge.alert-low { background: #28a745; }
        .badge.alert-medium { background: #ffc107; }
        .badge.alert-high { background: #dc3545; }
        
        .no-messages {
            text-align: center;
            color: #999;
            padding: 40px;
        }
        
        .refresh-btn {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 8px;
            font-size: 1em;
            cursor: pointer;
            margin: 20px auto;
            display: block;
            transition: background 0.3s;
        }
        
        .refresh-btn:hover {
            background: #5568d3;
        }
        
        .auto-refresh {
            text-align: center;
            color: white;
            margin: 10px 0;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚨 TrapEyes Dashboard</h1>
            <p>Sistema de Monitoramento em Tempo Real</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <h3>Total de Mensagens</h3>
                <div class="value" id="total-messages">0</div>
            </div>
            <div class="stat-card">
                <h3>Erros</h3>
                <div class="value" id="errors">0</div>
            </div>
            <div class="stat-card">
                <h3>Status</h3>
                <div class="value" style="color: #28a745;">●</div>
            </div>
        </div>
        
        <div class="auto-refresh">
            🔄 Atualização automática a cada 5 segundos
        </div>
        
        <button class="refresh-btn" onclick="loadMessages()">Atualizar Agora</button>
        
        <div class="messages-container" id="messages">
            <div class="no-messages">Carregando mensagens...</div>
        </div>
    </div>

    <script>
        let lastMessageCount = 0;
        
        function formatDate(dateString) {
            const date = new Date(dateString);
            return date.toLocaleString('pt-BR');
        }
        
        function createMessageCard(message, isNew = false) {
            const card = document.createElement('div');
            card.className = 'message-card' + (isNew ? ' new' : '');
            
            let metaHtml = '';
            if (message.device_id || message.location || message.alert_level) {
                metaHtml = '<div class="message-meta">';
                if (message.device_id) metaHtml += `<span class="badge">📱 ${message.device_id}</span>`;
                if (message.location) metaHtml += `<span class="badge">📍 ${message.location}</span>`;
                if (message.alert_level) {
                    const alertClass = `alert-${message.alert_level}`;
                    metaHtml += `<span class="badge ${alertClass}">⚠️ ${message.alert_level.toUpperCase()}</span>`;
                }
                if (message.temperature) metaHtml += `<span class="badge">🌡️ ${message.temperature}°C</span>`;
                if (message.humidity) metaHtml += `<span class="badge">💧 ${message.humidity}%</span>`;
                metaHtml += '</div>';
            }
            
            card.innerHTML = `
                <div class="message-header">
                    <div class="message-title">${message.message || 'Nova mensagem'}</div>
                    <div class="message-time">${formatDate(message.timestamp)}</div>
                </div>
                <div class="message-content">
                    ${JSON.stringify(message, null, 2).substring(0, 200)}...
                </div>
                ${metaHtml}
            `;
            
            return card;
        }
        
        async function loadMessages() {
            try {
                const response = await fetch('/api/messages');
                const data = await response.json();
                
                // Atualizar estatísticas
                document.getElementById('total-messages').textContent = data.stats.total_messages;
                document.getElementById('errors').textContent = data.stats.errors;
                
                const messagesDiv = document.getElementById('messages');
                
                if (data.messages.length === 0) {
                    messagesDiv.innerHTML = '<div class="no-messages">Nenhuma mensagem recebida ainda.</div>';
                    return;
                }
                
                // Verificar se há novas mensagens
                const isNewBatch = data.messages.length > lastMessageCount;
                lastMessageCount = data.messages.length;
                
                messagesDiv.innerHTML = '';
                data.messages.reverse().forEach((message, index) => {
                    const isNew = isNewBatch && index === 0;
                    messagesDiv.appendChild(createMessageCard(message, isNew));
                });
                
            } catch (error) {
                console.error('Erro ao carregar mensagens:', error);
            }
        }
        
        // Carregar mensagens ao iniciar
        loadMessages();
        
        // Atualizar automaticamente a cada 5 segundos
        setInterval(loadMessages, 5000);
    </script>
</body>
</html>
    """
    return render_template_string(html)

@app.route('/api/messages', methods=['GET'])
def get_messages():
    """Retorna lista de mensagens armazenadas"""
    try:
        messages_list = list(messages_storage)
        
        return jsonify({
            "success": True,
            "messages": messages_list,
            "count": len(messages_list),
            "stats": stats
        }), 200
        
    except Exception as e:
        logger.error(f"💥 Erro ao listar mensagens: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/messages', methods=['POST'])
def receive_message():
    """
    Recebe mensagem via POST e armazena
    
    Payload esperado:
    {
        "message": "Texto da mensagem",
        "device_id": "sensor-01",
        "location": "Sala 1",
        "temperature": 25.5,
        "humidity": 60,
        "alert_level": "high"  // low, medium, high
    }
    """
    try:
        stats["total_messages"] += 1
        
        # Validar JSON
        data = request.get_json()
        if not data:
            logger.warning("❌ JSON inválido ou ausente")
            return jsonify({"success": False, "error": "JSON inválido"}), 400
        
        # Log da requisição
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        logger.info(f"📨 Mensagem recebida de {client_ip}")
        
        # Adicionar timestamp
        message_data = {
            **data,
            "timestamp": datetime.now().isoformat(),
            "source_ip": client_ip
        }
        
        # Armazenar mensagem
        messages_storage.append(message_data)
        logger.info(f"💾 Mensagem armazenada (total: {len(messages_storage)})")
        
        return jsonify({
            "success": True,
            "message": "Mensagem recebida com sucesso",
            "stored": True,
            "message_id": len(messages_storage) - 1
        }), 200
        
    except Exception as e:
        stats["errors"] += 1
        logger.error(f"💥 Erro ao processar mensagem: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Retorna estatísticas do servidor"""
    uptime = datetime.now() - stats["start_time"]
    
    return jsonify({
        "success": True,
        "stats": {
            **stats,
            "uptime_seconds": int(uptime.total_seconds()),
            "messages_stored": len(messages_storage),
            "max_messages": MAX_MESSAGES
        }
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check para monitoramento"""
    return jsonify({
        "status": "healthy",
        "service": "trapeyes-server",
        "timestamp": datetime.now().isoformat()
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": "Endpoint não encontrado"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"success": False, "error": "Erro interno do servidor"}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚨 TRAPEYES MESSAGE SERVER")
    print("="*60)
    print(f" Porta: {PORT}")
    print(f"💾 Máximo de mensagens: {MAX_MESSAGES}")
    print()
    print("📋 Endpoints:")
    print(f"  - GET  http://localhost:{PORT}/         (Dashboard)")
    print(f"  - POST http://localhost:{PORT}/api/messages (Receber mensagem)")
    print(f"  - GET  http://localhost:{PORT}/api/messages (Listar mensagens)")
    print(f"  - GET  http://localhost:{PORT}/api/stats (Estatísticas)")
    print()
    print("🚀 Servidor iniciado!")
    print("="*60)
    
    app.run(
        host='0.0.0.0',
        port=PORT,
        debug=os.getenv("DEBUG", "false").lower() == "true"
    )