#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🗑️  Script para apagar todos os registros do TrapEyes
=====================================================

Este script envia uma requisição DELETE para o servidor
para apagar todas as mensagens armazenadas.

Uso:
    python3 clear_messages.py
    
    ou
    
    ./clear_messages.py
"""

import requests
import sys
import os

# Configurações
PORT = os.getenv("PORT", "5000")
HOST = os.getenv("HOST", "localhost")
BASE_URL = f"http://{HOST}:{PORT}"

def clear_messages():
    """Apaga todas as mensagens do servidor"""
    try:
        print("🗑️  Apagando todas as mensagens...")
        print(f"📡 Conectando em: {BASE_URL}/api/messages")
        
        response = requests.delete(f"{BASE_URL}/api/messages", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            count = data.get("deleted_count", 0)
            print(f"✅ Sucesso! {count} mensagens foram apagadas.")
            return 0
        else:
            print(f"❌ Erro: {response.status_code}")
            print(f"   {response.text}")
            return 1
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Erro: Não foi possível conectar ao servidor em {BASE_URL}")
        print("   Verifique se o servidor está rodando.")
        return 1
        
    except requests.exceptions.Timeout:
        print("❌ Erro: Timeout ao conectar com o servidor")
        return 1
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return 1

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🗑️  TRAPEYES - LIMPAR REGISTROS")
    print("="*60)
    print()
    
    exit_code = clear_messages()
    
    print()
    print("="*60)
    sys.exit(exit_code)
