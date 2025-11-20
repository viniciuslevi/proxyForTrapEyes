#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configurações do TrapEyes
"""
import os

# Configurações do Servidor
PORT = int(os.getenv("PORT", "8080"))
MAX_MESSAGES = int(os.getenv("MAX_MESSAGES", "1000"))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Thresholds de Diagnóstico
OCUPACAO_EXCESSIVA_THRESHOLD = float(os.getenv("OCUPACAO_EXCESSIVA_THRESHOLD", "20"))
ANORMAL_OCUPACAO_THRESHOLD = float(os.getenv("ANORMAL_OCUPACAO_THRESHOLD", "30"))
ANORMAL_MOSCAS_THRESHOLD = int(os.getenv("ANORMAL_MOSCAS_THRESHOLD", "50"))

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

