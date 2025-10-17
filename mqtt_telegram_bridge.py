#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌉 Ponte AWS IoT Core ↔ Telegram Bot
===================================

Este serviço conecta ao AWS IoT Core via MQTT e encaminha
mensagens recebidas para o Telegram Bot via HTTPS.

Uso:
    export TELEGRAM_TOKEN="seu_bot_token_aqui"
    export AWS_IOT_ENDPOINT="a25833zo7tzuak-ats.iot.us-east-1.amazonaws.com"
    export MQTT_TOPIC="trapeyes"  # opcional
    python3 mqtt_telegram_bridge.py

Fluxo:
    Dispositivo IoT → AWS IoT Core (MQTT) → Este Script → Telegram Bot (HTTPS)
"""

import json
import logging
import os
import ssl
import sys
import time
from datetime import datetime
from threading import Thread

import paho.mqtt.client as mqtt
import requests

# Configuração de logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurações AWS IoT
AWS_IOT_ENDPOINT = os.getenv("AWS_IOT_ENDPOINT", "a25833zo7tzuak-ats.iot.us-east-1.amazonaws.com")
AWS_IOT_PORT = int(os.getenv("AWS_IOT_PORT", "8883"))

# Certificados e chaves das variáveis de ambiente
AWS_DEVICE_CERT = os.getenv("AWS_DEVICE_CERT")
AWS_PRIVATE_KEY = os.getenv("AWS_PRIVATE_KEY") 
AWS_ROOT_CA = os.getenv("AWS_ROOT_CA")

# Configurações MQTT
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "trapeyes")
CLIENT_ID = os.getenv("CLIENT_ID", f"telegram-bridge-{int(time.time())}")
MQTT_KEEPALIVE = int(os.getenv("MQTT_KEEPALIVE", "60"))
MQTT_TIMEOUT = int(os.getenv("MQTT_TIMEOUT", "30"))
MQTT_QOS = int(os.getenv("MQTT_QOS", "1"))

# Configurações Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    logger.error("❌ ERRO: Defina TELEGRAM_TOKEN como variável de ambiente")
    sys.exit(1)

DEFAULT_CHAT_ID = os.getenv("DEFAULT_CHAT_ID")  # Chat ID padrão (opcional)

# URLs Telegram
TELEGRAM_BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Estatísticas
stats = {
    "mqtt_connected": False,
    "messages_received": 0,
    "messages_sent": 0,
    "errors": 0,
    "start_time": datetime.now()
}

class TelegramSender:
    """Classe para enviar mensagens para o Telegram"""
    
    def __init__(self):
        self.session = requests.Session()
    
    def send_message(self, chat_id, text, parse_mode="HTML"):
        """
        Envia mensagem para o Telegram
        
        Args:
            chat_id (str): ID do chat de destino
            text (str): Texto da mensagem
            parse_mode (str): Modo de formatação (HTML, Markdown)
        
        Returns:
            bool: True se enviado com sucesso
        """
        try:
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": parse_mode
            }
            
            response = self.session.post(
                f"{TELEGRAM_BASE_URL}/sendMessage",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('ok'):
                    stats["messages_sent"] += 1
                    logger.info(f"✅ Mensagem enviada para {chat_id}")
                    return True
                else:
                    logger.error(f"❌ Erro Telegram: {result}")
                    stats["errors"] += 1
                    return False
            else:
                logger.error(f"❌ HTTP {response.status_code}: {response.text}")
                stats["errors"] += 1
                return False
                
        except Exception as e:
            logger.error(f"💥 Erro ao enviar mensagem: {e}")
            stats["errors"] += 1
            return False

class MQTTTelegramBridge:
    """Ponte entre MQTT (AWS IoT) e Telegram"""
    
    def __init__(self):
        self.telegram = TelegramSender()
        self.mqtt_client = None
        self.running = False
        
    def on_connect(self, client, userdata, flags, rc):
        """Callback quando conecta ao MQTT"""
        if rc == 0:
            stats["mqtt_connected"] = True
            logger.info(f"🔗 Conectado ao AWS IoT Core: {AWS_IOT_ENDPOINT}")
            
            # Inscrever no tópico
            result, mid = client.subscribe(MQTT_TOPIC, qos=MQTT_QOS)  # QoS configurável
            if result == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"📡 Inscrito no tópico: {MQTT_TOPIC} (MID: {mid})")
            else:
                logger.error(f"❌ Erro ao se inscrever no tópico: {result}")
            
        else:
            stats["mqtt_connected"] = False
            error_messages = {
                1: "Versão de protocolo incorreta",
                2: "Client ID inválido",
                3: "Servidor não disponível",
                4: "Usuário/senha incorretos",
                5: "Não autorizado"
            }
            error_msg = error_messages.get(rc, f"Erro desconhecido: {rc}")
            logger.error(f"❌ Falha na conexão MQTT. Código {rc}: {error_msg}")
    
    def on_disconnect(self, client, userdata, rc):
        """Callback quando desconecta do MQTT"""
        stats["mqtt_connected"] = False
        if rc != 0:
            logger.warning(f"⚠️  Desconectado inesperadamente do MQTT. Código: {rc}")
            # Implementar lógica de reconexão automática
            self.reconnect_mqtt()
        else:
            logger.info("ℹ️  Desconectado do MQTT de forma normal")
    
    def on_log(self, client, userdata, level, buf):
        """Callback para logs do cliente MQTT"""
        # Filtrar apenas logs importantes para evitar spam
        if level <= mqtt.MQTT_LOG_WARNING:
            if "PINGRESP" not in buf and "PINGREQ" not in buf:
                logger.debug(f"MQTT Log ({level}): {buf}")
    
    def reconnect_mqtt(self):
        """Tenta reconectar ao MQTT com backoff exponencial"""
        max_retries = 5
        base_delay = 2
        
        for attempt in range(max_retries):
            try:
                delay = base_delay * (2 ** attempt)  # Backoff exponencial
                logger.info(f"🔄 Tentativa de reconexão {attempt + 1}/{max_retries} em {delay}s...")
                time.sleep(delay)
                
                if self.mqtt_client:
                    self.mqtt_client.reconnect()
                    return True
                    
            except Exception as e:
                logger.warning(f"⚠️  Falha na tentativa {attempt + 1}: {e}")
        
        logger.error("❌ Todas as tentativas de reconexão falharam")
        return False
    
    def on_message(self, client, userdata, msg):
        """
        Callback quando recebe mensagem MQTT
        
        Formato esperado da mensagem:
        {
            "chat_id": "123456789",
            "message": "Temperatura: 25°C",
            "sensor": "temp01",
            "timestamp": "2024-01-01T12:00:00Z"
        }
        
        OU mensagem simples (usando chat padrão):
        {
            "message": "Alerta: Temperatura alta!",
            "value": 35.5
        }
        """
        try:
            stats["messages_received"] += 1
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            logger.info(f"📨 Mensagem recebida do tópico '{topic}': {payload[:100]}...")
            
            # Tentar fazer parse JSON
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                # Se não é JSON, tratar como texto simples
                data = {"message": payload}
            
            # Determinar chat_id
            chat_id = data.get('chat_id', DEFAULT_CHAT_ID)
            if not chat_id:
                logger.error("❌ chat_id não encontrado na mensagem e DEFAULT_CHAT_ID não configurado")
                stats["errors"] += 1
                return
            
            # Construir mensagem para Telegram
            message_text = self._build_telegram_message(data, topic)
            
            # Enviar para Telegram
            success = self.telegram.send_message(chat_id, message_text)
            
            if success:
                logger.info(f"✅ Mensagem MQTT→Telegram enviada com sucesso")
            else:
                logger.error(f"❌ Falha ao enviar mensagem para Telegram")
                
        except Exception as e:
            logger.error(f"💥 Erro ao processar mensagem MQTT: {e}")
            stats["errors"] += 1
    
    def _build_telegram_message(self, data, topic):
        """
        Constrói mensagem formatada para o Telegram
        
        Args:
            data (dict): Dados da mensagem MQTT
            topic (str): Tópico MQTT de origem
        
        Returns:
            str: Mensagem formatada em HTML
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Mensagem principal
        main_message = data.get('message', 'Dados recebidos via IoT')
        
        # Construir mensagem HTML
        html_message = f"<b>🤖 AWS IoT → Telegram</b>\n\n"
        html_message += f"📢 <b>{main_message}</b>\n\n"
        
        # Adicionar campos extras
        extras = []
        for key, value in data.items():
            if key not in ['message', 'chat_id']:
                if key == 'timestamp':
                    extras.append(f"🕐 <b>Timestamp:</b> {value}")
                elif key == 'sensor':
                    extras.append(f"📡 <b>Sensor:</b> {value}")
                elif key == 'value':
                    extras.append(f"📊 <b>Valor:</b> {value}")
                elif key == 'temperature':
                    extras.append(f"🌡️ <b>Temperatura:</b> {value}°C")
                elif key == 'humidity':
                    extras.append(f"💧 <b>Umidade:</b> {value}%")
                elif key == 'status':
                    extras.append(f"🔄 <b>Status:</b> {value}")
                else:
                    extras.append(f"📋 <b>{key.title()}:</b> {value}")
        
        if extras:
            html_message += "\n".join(extras) + "\n\n"
        
        # Informações técnicas
        html_message += f"📡 <b>Tópico:</b> <code>{topic}</code>\n"
        html_message += f"🕐 <b>Recebido:</b> {timestamp}"
        
        return html_message
    
    def setup_mqtt_client(self):
        """Configura cliente MQTT com TLS para AWS IoT usando credenciais do .env"""
        try:
            # Verificar se as credenciais estão definidas
            if not AWS_DEVICE_CERT or not AWS_PRIVATE_KEY or not AWS_ROOT_CA:
                logger.error("❌ Credenciais AWS IoT não encontradas nas variáveis de ambiente")
                logger.error("   Verifique se AWS_DEVICE_CERT, AWS_PRIVATE_KEY e AWS_ROOT_CA estão definidas")
                return False
            
            # Criar arquivos temporários para os certificados
            import tempfile
            
            # Criar arquivo temporário para o certificado do dispositivo
            with tempfile.NamedTemporaryFile(mode='w', suffix='.crt', delete=False) as cert_file:
                cert_file.write(AWS_DEVICE_CERT)
                device_cert_path = cert_file.name
            
            # Criar arquivo temporário para a chave privada
            with tempfile.NamedTemporaryFile(mode='w', suffix='.key', delete=False) as key_file:
                key_file.write(AWS_PRIVATE_KEY)
                private_key_path = key_file.name
            
            # Criar arquivo temporário para o Root CA
            with tempfile.NamedTemporaryFile(mode='w', suffix='.pem', delete=False) as ca_file:
                ca_file.write(AWS_ROOT_CA)
                root_ca_path = ca_file.name
            
            # Criar cliente MQTT com configurações otimizadas
            self.mqtt_client = mqtt.Client(
                client_id=CLIENT_ID,
                clean_session=True,  # Limpa sessão anterior
                protocol=mqtt.MQTTv311  # Força protocolo específico
            )
            
            # Configurar callbacks
            self.mqtt_client.on_connect = self.on_connect
            self.mqtt_client.on_disconnect = self.on_disconnect
            self.mqtt_client.on_message = self.on_message
            self.mqtt_client.on_log = self.on_log  # Adicionar callback de log
            
            # Configurar timeouts e keep-alive
            self.mqtt_client.connect_async_timeout = MQTT_TIMEOUT  # Timeout de conexão
            self.mqtt_client.keepalive = MQTT_KEEPALIVE  # Keep-alive configurável
            
            # Configurar TLS/SSL com validação mais rigorosa
            context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
            context.check_hostname = False  # AWS IoT usa certificados específicos
            context.verify_mode = ssl.CERT_REQUIRED
            context.load_verify_locations(root_ca_path)
            context.load_cert_chain(device_cert_path, private_key_path)
            
            # Configurar TLS versão mínima
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            
            self.mqtt_client.tls_set_context(context)
            
            # Limpar arquivos temporários
            os.unlink(device_cert_path)
            os.unlink(private_key_path)
            os.unlink(root_ca_path)
            
            logger.info("🔐 Cliente MQTT configurado com TLS usando credenciais do .env")
            return True
            
        except Exception as e:
            logger.error(f"💥 Erro ao configurar cliente MQTT: {e}")
            return False
    
    def start(self):
        """Inicia a ponte MQTT-Telegram com configurações robustas"""
        logger.info("🚀 Iniciando ponte AWS IoT Core ↔ Telegram...")
        
        # Configurar cliente MQTT
        if not self.setup_mqtt_client():
            logger.error("❌ Falha ao configurar cliente MQTT")
            return False
        
        try:
            # Conectar ao AWS IoT Core com timeout maior
            logger.info(f"🔗 Conectando a {AWS_IOT_ENDPOINT}:{AWS_IOT_PORT}...")
            
            # Configurar reconexão automática
            self.mqtt_client.reconnect_delay_set(min_delay=1, max_delay=120)
            
            # Tentar conectar com timeout específico
            result = self.mqtt_client.connect(AWS_IOT_ENDPOINT, AWS_IOT_PORT, keepalive=MQTT_KEEPALIVE)
            
            if result != mqtt.MQTT_ERR_SUCCESS:
                logger.error(f"❌ Erro na conexão inicial: {result}")
                return False
            
            # Iniciar loop não bloqueante
            self.running = True
            self.mqtt_client.loop_start()
            
            # Aguardar conexão efetiva (configurável)
            connection_timeout = MQTT_TIMEOUT
            start_time = time.time()
            
            while not stats["mqtt_connected"] and (time.time() - start_time) < connection_timeout:
                time.sleep(0.5)
            
            if stats["mqtt_connected"]:
                logger.info("✅ Ponte iniciada com sucesso!")
                return True
            else:
                logger.error("❌ Timeout na conexão MQTT")
                return False
            
        except Exception as e:
            logger.error(f"💥 Erro ao iniciar ponte: {e}")
            return False
    
    def stop(self):
        """Para a ponte"""
        self.running = False
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        logger.info("🛑 Ponte parada")

def print_status():
    """Imprime status da aplicação"""
    uptime = datetime.now() - stats["start_time"]
    
    print("\n" + "="*60)
    print("📊 STATUS DA PONTE AWS IoT ↔ TELEGRAM")
    print("="*60)
    print(f"🔗 MQTT Conectado: {'✅ Sim' if stats['mqtt_connected'] else '❌ Não'}")
    print(f"📨 Mensagens recebidas: {stats['messages_received']}")
    print(f"✅ Mensagens enviadas: {stats['messages_sent']}")
    print(f"❌ Erros: {stats['errors']}")
    print(f"⏱️  Uptime: {uptime}")
    print(f"📡 Tópico: {MQTT_TOPIC}")
    print(f"🏷️  Client ID: {CLIENT_ID}")
    print("="*60)

def main():
    """Função principal"""
    print("\n" + "="*60)
    print("🌉 PONTE AWS IoT CORE ↔ TELEGRAM BOT")
    print("="*60)
    print(f"📡 Endpoint: {AWS_IOT_ENDPOINT}:{AWS_IOT_PORT}")
    print(f"📢 Tópico: {MQTT_TOPIC}")
    print(f"🤖 Bot Token: {'✅ Configurado' if TELEGRAM_TOKEN else '❌ Não configurado'}")
    print(f"💬 Chat padrão: {DEFAULT_CHAT_ID or '❌ Não configurado'}")
    print("="*60)
    
    # Criar e iniciar ponte
    bridge = MQTTTelegramBridge()
    
    if not bridge.start():
        logger.error("❌ Falha ao iniciar ponte")
        sys.exit(1)
    
    try:
        # Loop principal
        while bridge.running:
            time.sleep(30)  # Status a cada 30 segundos
            print_status()
            
    except KeyboardInterrupt:
        logger.info("⚠️  Interrupção detectada (Ctrl+C)")
    except Exception as e:
        logger.error(f"💥 Erro inesperado: {e}")
    finally:
        bridge.stop()
        print("\n🏁 Ponte finalizada")

if __name__ == "__main__":
    main()