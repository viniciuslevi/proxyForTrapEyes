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
    """Página inicial com interface para visualizar detecções de moscas"""
    html = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TrapEyes - Sistema de Detecção de Moscas com IA</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        :root {
            --primary: #2563eb;
            --primary-dark: #1e40af;
            --secondary: #8b5cf6;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --bg-dark: #0f172a;
            --bg-card: #1e293b;
            --bg-card-hover: #334155;
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --border: #334155;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--bg-dark);
            color: var(--text-primary);
            min-height: 100vh;
            line-height: 1.6;
        }
        
        /* Header */
        .navbar {
            background: var(--bg-card);
            border-bottom: 1px solid var(--border);
            padding: 1rem 2rem;
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(10px);
        }
        
        .navbar-content {
            max-width: 1600px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .logo-icon {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
        }
        
        .logo h1 {
            font-size: 1.5rem;
            font-weight: 700;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .logo-subtitle {
            font-size: 0.75rem;
            color: var(--text-secondary);
            margin-top: -8px;
        }
        
        .nav-stats {
            display: flex;
            gap: 2rem;
            align-items: center;
        }
        
        .nav-stat {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
        }
        
        .nav-stat-label {
            font-size: 0.75rem;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .nav-stat-value {
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text-primary);
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: rgba(16, 185, 129, 0.1);
            border-radius: 20px;
            border: 1px solid var(--success);
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            background: var(--success);
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        /* Container */
        .container {
            max-width: 1600px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        /* Grid Layouts */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        /* Cards */
        .card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 1.5rem;
            transition: all 0.3s ease;
            animation: fadeInUp 0.5s ease-out;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .card:hover {
            border-color: var(--primary);
            transform: translateY(-2px);
            box-shadow: 0 10px 40px rgba(37, 99, 235, 0.2);
        }
        
        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .card-title {
            font-size: 0.875rem;
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .card-icon {
            width: 36px;
            height: 36px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
        }
        
        /* Stat Card */
        .stat-value {
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0.5rem 0;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .stat-change {
            display: flex;
            align-items: center;
            gap: 4px;
            font-size: 0.875rem;
            margin-top: 0.5rem;
        }
        
        .stat-change.positive { color: var(--success); }
        .stat-change.negative { color: var(--danger); }
        
        .stat-description {
            font-size: 0.875rem;
            color: var(--text-secondary);
            margin-top: 0.5rem;
        }
        
        /* Chart Container */
        .chart-container {
            position: relative;
            height: 300px;
            margin-top: 1rem;
        }
        
        .chart-container.large {
            height: 400px;
        }
        
        /* Table */
        .table-container {
            overflow-x: auto;
            margin-top: 1rem;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th {
            text-align: left;
            padding: 0.75rem 1rem;
            font-size: 0.75rem;
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            border-bottom: 1px solid var(--border);
        }
        
        td {
            padding: 1rem;
            border-bottom: 1px solid var(--border);
        }
        
        tr:hover {
            background: var(--bg-card-hover);
        }
        
        /* Badge */
        .badge {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .badge-success {
            background: rgba(16, 185, 129, 0.1);
            color: var(--success);
            border: 1px solid var(--success);
        }
        
        .badge-warning {
            background: rgba(245, 158, 11, 0.1);
            color: var(--warning);
            border: 1px solid var(--warning);
        }
        
        .badge-danger {
            background: rgba(239, 68, 68, 0.1);
            color: var(--danger);
            border: 1px solid var(--danger);
        }
        
        .badge-primary {
            background: rgba(37, 99, 235, 0.1);
            color: var(--primary);
            border: 1px solid var(--primary);
        }
        
        /* Device Status */
        .device-list {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
            margin-top: 1rem;
        }
        
        .device-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem;
            background: rgba(255, 255, 255, 0.02);
            border-radius: 8px;
            border: 1px solid transparent;
            transition: all 0.2s;
        }
        
        .device-item:hover {
            border-color: var(--border);
            background: rgba(255, 255, 255, 0.05);
        }
        
        .device-info {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .device-status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        .device-status-dot.active { background: var(--success); }
        .device-status-dot.warning { background: var(--warning); }
        .device-status-dot.error { background: var(--danger); }
        
        .device-name {
            font-weight: 500;
        }
        
        .device-location {
            font-size: 0.875rem;
            color: var(--text-secondary);
        }
        
        .device-metrics {
            display: flex;
            gap: 1rem;
            font-size: 0.875rem;
        }
        
        .metric {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
        }
        
        .metric-label {
            color: var(--text-secondary);
            font-size: 0.75rem;
        }
        
        .metric-value {
            font-weight: 600;
        }
        
        /* Loading */
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255, 255, 255, 0.1);
            border-radius: 50%;
            border-top-color: var(--primary);
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        /* Responsive */
        @media (max-width: 1024px) {
            .charts-grid {
                grid-template-columns: 1fr;
            }
            
            .nav-stats {
                gap: 1rem;
            }
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 1rem;
            }
            
            .navbar {
                padding: 1rem;
            }
            
            .nav-stats {
                display: none;
            }
            
            .stats-grid {
                grid-template-columns: 1fr;
            }
        }
        
        /* Tooltip */
        .tooltip {
            position: relative;
            display: inline-block;
        }
        
        .tooltip:hover::after {
            content: attr(data-tooltip);
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            padding: 8px 12px;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 6px;
            font-size: 0.875rem;
            white-space: nowrap;
            z-index: 1000;
        }
    </style>
</head>
<body>
    <!-- Navbar -->
    <nav class="navbar">
        <div class="navbar-content">
            <div class="logo">
                <div class="logo-icon">🦟</div>
                <div>
                    <h1>TrapEyes - Detecção de Moscas IA</h1>
                    <div class="logo-subtitle">Sistema de Monitoramento Inteligente</div>
                </div>
            </div>
            <div class="nav-stats">
                <div class="nav-stat">
                    <span class="nav-stat-label">Moscas Detectadas</span>
                    <span class="nav-stat-value" id="nav-total">0</span>
                </div>
                <div class="nav-stat">
                    <span class="nav-stat-label">Dispositivos LoRa</span>
                    <span class="nav-stat-value" id="nav-devices">0</span>
                </div>
                <div class="status-indicator">
                    <div class="status-dot"></div>
                    <span>Sistema Online</span>
                </div>
            </div>
        </div>
    </nav>

    <!-- Main Container -->
    <div class="container">
        <!-- Stats Grid -->
        <div class="stats-grid">
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Total de Moscas Detectadas</span>
                    <div class="card-icon" style="background: rgba(37, 99, 235, 0.1);">🦟</div>
                </div>
                <div class="stat-value" id="total-flies">0</div>
                <div class="stat-change positive">
                    <span>↗</span>
                    <span id="flies-change">+15%</span>
                </div>
                <div class="stat-description">Todas as capturas</div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Capturas Realizadas</span>
                    <div class="card-icon" style="background: rgba(16, 185, 129, 0.1);">📸</div>
                </div>
                <div class="stat-value" id="total-captures">0</div>
                <div class="stat-change positive">
                    <span>↗</span>
                    <span id="captures-change">+8</span>
                </div>
                <div class="stat-description">Última hora</div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Confiança Média</span>
                    <div class="card-icon" style="background: rgba(245, 158, 11, 0.1);">🎯</div>
                </div>
                <div class="stat-value" id="avg-confidence">0%</div>
                <div class="stat-change positive">
                    <span>↗</span>
                    <span>+3%</span>
                </div>
                <div class="stat-description">Modelo de IA</div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Dispositivos LoRa</span>
                    <div class="card-icon" style="background: rgba(139, 92, 246, 0.1);">📡</div>
                </div>
                <div class="stat-value" id="lora-devices">0</div>
                <div class="stat-change positive">
                    <span>●</span>
                    <span>Online</span>
                </div>
                <div class="stat-description">Sensores ativos</div>
            </div>
        </div>

        <!-- Secondary Stats -->
        <div class="stats-grid" style="grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); margin-bottom: 2rem;">
            <div class="card" style="padding: 1rem;">
                <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase;">Ocupação Média</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: var(--warning); margin: 0.25rem 0;" id="avg-ocupacao">0%</div>
                <div style="font-size: 0.75rem; color: var(--text-secondary);">Área ocupada</div>
            </div>
            <div class="card" style="padding: 1rem;">
                <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase;">Tempo Inferência</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: var(--secondary); margin: 0.25rem 0;" id="avg-inference">0ms</div>
                <div style="font-size: 0.75rem; color: var(--text-secondary);">Média do modelo</div>
            </div>
            <div class="card" style="padding: 1rem;">
                <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase;">Ocupação Excessiva</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: var(--warning); margin: 0.25rem 0;" id="count-excessiva">0</div>
                <div style="font-size: 0.75rem; color: var(--text-secondary);">Alertas</div>
            </div>
            <div class="card" style="padding: 1rem;">
                <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase;">Detecções Anormais</div>
                <div style="font-size: 1.5rem; font-weight: 700; color: var(--danger); margin: 0.25rem 0;" id="count-anormal">0</div>
                <div style="font-size: 0.75rem; color: var(--text-secondary);">Situações críticas</div>
            </div>
        </div>

        <!-- Charts Grid -->
        <div class="charts-grid">
            <div class="card">
                <div class="card-header">
                    <span class="card-title">🦟 Moscas Detectadas por Hora</span>
                </div>
                <div class="chart-container">
                    <canvas id="detectionsChart"></canvas>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <span class="card-title">🎯 Confiança Média do Modelo IA</span>
                </div>
                <div class="chart-container">
                    <canvas id="confidenceChart"></canvas>
                </div>
            </div>
        </div>

        <div class="charts-grid">
            <div class="card">
                <div class="card-header">
                    <span class="card-title">📊 Ocupação por Captura (%)</span>
                </div>
                <div class="chart-container">
                    <canvas id="occupancyChart"></canvas>
                </div>
            </div>
            
            <div class="card">
                <div class="card-header">
                    <span class="card-title">⚡ Tempo de Inferência (ms)</span>
                </div>
                <div class="chart-container">
                    <canvas id="inferenceChart"></canvas>
                </div>
            </div>
        </div>

        <!-- Devices Status -->
        <div class="card">
            <div class="card-header">
                <span class="card-title">📡 Status dos Dispositivos LoRa</span>
            </div>
            <div class="device-list" id="device-list">
                <div class="loading"></div>
            </div>
        </div>

        <!-- Recent Detections -->
        <div class="card">
            <div class="card-header">
                <span class="card-title">🦟 Detecções Recentes</span>
            </div>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>Dispositivo LoRa</th>
                            <th>Moscas (Status)</th>
                            <th>Confiança</th>
                            <th>Limiar</th>
                            <th>Ocupação/BBoxes</th>
                        </tr>
                    </thead>
                    <tbody id="detections-table">
                        <tr>
                            <td colspan="6" style="text-align: center; color: var(--text-secondary);">
                                Carregando detecções...
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        // Configuração global dos gráficos
        Chart.defaults.color = '#94a3b8';
        Chart.defaults.borderColor = '#334155';
        Chart.defaults.font.family = 'Inter';
        
        // Dados para visualização
        let detectionsData = [];
        let confidenceData = [];
        let loraDevices = {};
        let devicesData = [
            { id: 'LORA-001', location: 'Área Norte', flies: 0, captures: 0, status: 'active', avgConf: 0 },
            { id: 'LORA-002', location: 'Área Sul', flies: 0, captures: 0, status: 'active', avgConf: 0 },
            { id: 'LORA-003', location: 'Estufa Principal', flies: 0, captures: 0, status: 'active', avgConf: 0 },
            { id: 'LORA-004', location: 'Armazenamento', flies: 0, captures: 0, status: 'active', avgConf: 0 },
            { id: 'LORA-005', location: 'Entrada', flies: 0, captures: 0, status: 'active', avgConf: 0 }
        ];
        
        // Gerar dados iniciais simulados
        // Dados dos graficos serao carregados da API (apenas dados reais)
        
        // Gráfico de Detecções por Hora
        const detectionsCtx = document.getElementById('detectionsChart').getContext('2d');
        const detectionsChart = new Chart(detectionsCtx, {
            type: 'line',
            data: {
                labels: detectionsData.map(d => d.time),
                datasets: [{
                    label: 'Moscas Detectadas',
                    data: detectionsData.map(d => d.count),
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 7,
                    pointBackgroundColor: '#2563eb',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#1e293b',
                        borderColor: '#334155',
                        borderWidth: 1,
                        padding: 12,
                        displayColors: false,
                        callbacks: {
                            label: (context) => context.parsed.y + ' moscas'
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: '#334155' },
                        ticks: {
                            callback: (value) => value + ' 🦟'
                        }
                    },
                    x: {
                        grid: { display: false }
                    }
                },
                animation: {
                    duration: 750,
                    easing: 'easeInOutQuart'
                }
            }
        });
        
        // Gráfico de Confiança
        const confidenceCtx = document.getElementById('confidenceChart').getContext('2d');
        const confidenceChart = new Chart(confidenceCtx, {
            type: 'line',
            data: {
                labels: confidenceData.map(d => d.time),
                datasets: [{
                    label: 'Confiança Média (%)',
                    data: confidenceData.map(d => d.value * 100),
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 7,
                    pointBackgroundColor: '#f59e0b',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#1e293b',
                        borderColor: '#334155',
                        borderWidth: 1,
                        padding: 12,
                        displayColors: false,
                        callbacks: {
                            label: (context) => context.parsed.y.toFixed(1) + '%'
                        }
                    }
                },
                scales: {
                    y: {
                        min: 0,
                        max: 100,
                        grid: { color: '#334155' },
                        ticks: {
                            callback: (value) => value + '%'
                        }
                    },
                    x: {
                        grid: { display: false }
                    }
                },
                animation: {
                    duration: 750,
                    easing: 'easeInOutQuart'
                }
            }
        });
        
        // Gráfico de Ocupação por Captura
        const occupancyCtx = document.getElementById('occupancyChart').getContext('2d');
        const occupancyChart = new Chart(occupancyCtx, {
            type: 'bar',
            data: {
                labels: ['Cap 1', 'Cap 2', 'Cap 3', 'Cap 4', 'Cap 5', 'Cap 6', 'Cap 7', 'Cap 8', 'Cap 9', 'Cap 10'],
                datasets: [{
                    label: 'Ocupação %',
                    data: [15, 8, 23, 12, 18, 7, 25, 11, 19, 14],
                    backgroundColor: 'rgba(139, 92, 246, 0.8)',
                    borderColor: '#8b5cf6',
                    borderWidth: 2,
                    borderRadius: 6,
                    hoverBackgroundColor: 'rgba(139, 92, 246, 1)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#1e293b',
                        borderColor: '#334155',
                        borderWidth: 1,
                        padding: 12,
                        displayColors: false,
                        callbacks: {
                            label: (context) => context.parsed.y + '%'
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        grid: { color: '#334155' },
                        ticks: {
                            callback: (value) => value + '%'
                        }
                    },
                    x: {
                        grid: { display: false }
                    }
                },
                animation: {
                    duration: 750,
                    easing: 'easeInOutQuart'
                }
            }
        });
        
        // Gráfico de Tempo de Inferência
        const inferenceCtx = document.getElementById('inferenceChart').getContext('2d');
        const inferenceChart = new Chart(inferenceCtx, {
            type: 'line',
            data: {
                labels: ['Cap 1', 'Cap 2', 'Cap 3', 'Cap 4', 'Cap 5', 'Cap 6', 'Cap 7', 'Cap 8', 'Cap 9', 'Cap 10'],
                datasets: [{
                    label: 'Tempo (ms)',
                    data: [87, 95, 112, 78, 89, 103, 92, 85, 98, 91],
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 7,
                    pointBackgroundColor: '#f59e0b',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        backgroundColor: '#1e293b',
                        borderColor: '#334155',
                        borderWidth: 1,
                        padding: 12,
                        displayColors: false,
                        callbacks: {
                            label: (context) => context.parsed.y.toFixed(1) + 'ms'
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: '#334155' },
                        ticks: {
                            callback: (value) => value + 'ms'
                        }
                    },
                    x: {
                        grid: { display: false }
                    }
                },
                animation: {
                    duration: 750,
                    easing: 'easeInOutQuart'
                }
            }
        });
        
        // Renderizar lista de dispositivos LoRa
        function renderDevices() {
            const deviceList = document.getElementById('device-list');
            deviceList.innerHTML = devicesData.map(device => `
                <div class="device-item">
                    <div class="device-info">
                        <div class="device-status-dot ${device.status}"></div>
                        <div>
                            <div class="device-name">📡 ${device.id}</div>
                            <div class="device-location">📍 ${device.location}</div>
                        </div>
                    </div>
                    <div class="device-metrics">
                        <div class="metric">
                            <span class="metric-label">Moscas Total</span>
                            <span class="metric-value">${device.flies || 0}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Capturas</span>
                            <span class="metric-value">${device.captures || 0}</span>
                        </div>
                        <div class="metric">
                            <span class="metric-label">Conf. Média</span>
                            <span class="metric-value">${device.avgConf || 0}%</span>
                        </div>
                    </div>
                </div>
            `).join('');
        }
        
        // Atualizar estatísticas
        function updateStats(data) {
            const captures = data.messages || [];
            
            // Total de moscas detectadas
            const totalFlies = captures.reduce((sum, cap) => {
                return sum + (cap.deteccoes?.total || 0);
            }, 0);
            
            // Total de capturas
            const totalCaptures = captures.length;
            
            // Dispositivos LoRa únicos
            const loraDevicesSet = new Set(captures.map(m => m.lora_id).filter(id => id));
            const loraDevicesCount = loraDevicesSet.size || devicesData.length;
            
            // Calcular confiança média
            let avgConfidence = 0;
            let confCount = 0;
            captures.forEach(cap => {
                if (cap.deteccoes?.confianca_media) {
                    avgConfidence += cap.deteccoes.confianca_media;
                    confCount++;
                }
            });
            avgConfidence = confCount > 0 ? ((avgConfidence / confCount) * 100).toFixed(1) : 0;
            
            // Atualizar dispositivos com dados reais
            devicesData.forEach(device => {
                const deviceCaptures = captures.filter(c => c.lora_id === device.id);
                device.captures = deviceCaptures.length;
                device.flies = deviceCaptures.reduce((sum, c) => sum + (c.deteccoes?.total || 0), 0);
                
                let devConfSum = 0;
                let devConfCount = 0;
                deviceCaptures.forEach(cap => {
                    if (cap.deteccoes?.confianca_media) {
                        devConfSum += cap.deteccoes.confianca_media;
                        devConfCount++;
                    }
                });
                device.avgConf = devConfCount > 0 ? ((devConfSum / devConfCount) * 100).toFixed(0) : 0;
            });
            
            // Calcular métricas de diagnóstico
            let countExcessiva = 0;
            let countAnormal = 0;
            let avgOcupacao = 0;
            let avgInferencia = 0;
            let inferCount = 0;
            
            captures.forEach(cap => {
                if (cap.diagnostico) {
                    if (cap.diagnostico.ocupacao_excessiva) countExcessiva++;
                    if (cap.diagnostico.anormal) countAnormal++;
                }
                if (cap.deteccoes?.ocupacao_pct) {
                    avgOcupacao += cap.deteccoes.ocupacao_pct;
                }
                if (cap.tempo_inferencia_ms) {
                    avgInferencia += cap.tempo_inferencia_ms;
                    inferCount++;
                }
            });
            
            avgOcupacao = captures.length > 0 ? (avgOcupacao / captures.length).toFixed(1) : 0;
            avgInferencia = inferCount > 0 ? (avgInferencia / inferCount).toFixed(1) : 0;
            
            document.getElementById('total-flies').textContent = totalFlies;
            document.getElementById('total-captures').textContent = totalCaptures;
            document.getElementById('avg-confidence').textContent = avgConfidence + '%';
            document.getElementById('lora-devices').textContent = loraDevicesCount;
            
            document.getElementById('avg-ocupacao').textContent = avgOcupacao + '%';
            document.getElementById('avg-inference').textContent = avgInferencia + 'ms';
            document.getElementById('count-excessiva').textContent = countExcessiva;
            document.getElementById('count-anormal').textContent = countAnormal;
            
            document.getElementById('nav-total').textContent = totalFlies;
            document.getElementById('nav-devices').textContent = loraDevicesCount;
        }
        
        // Renderizar tabela de detecções
        function renderDetectionsTable(detections) {
            const tbody = document.getElementById('detections-table');
            
            if (!detections || detections.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="6" style="text-align: center; color: var(--text-secondary);">
                            Nenhuma detecção recebida ainda
                        </td>
                    </tr>
                `;
                return;
            }
            
            tbody.innerHTML = detections.slice(-15).reverse().map(det => {
                const dataHora = det.timestamp || new Date().toLocaleString('pt-BR');
                const deteccoes = det.deteccoes || {};
                const diagnostico = det.diagnostico || {};
                
                // Dados das detecções
                const qtdFlies = deteccoes.total || 0;
                const confMedia = deteccoes.confianca_media ? (deteccoes.confianca_media * 100).toFixed(1) : '0';
                const limiarConf = deteccoes.limiar_confianca ? (deteccoes.limiar_confianca * 100).toFixed(0) : 'N/A';
                const ocupacao = deteccoes.ocupacao_pct ? deteccoes.ocupacao_pct.toFixed(1) : '0';
                const numItens = deteccoes.itens ? deteccoes.itens.length : 0;
                
                // Determinar badge por diagnóstico
                const badgeClass = diagnostico.anormal ? 'danger' : diagnostico.ocupacao_excessiva ? 'warning' : 'success';
                const statusIcon = diagnostico.anormal ? '🔴' : diagnostico.ocupacao_excessiva ? '🟡' : '🟢';
                
                return `
                    <tr>
                        <td>${dataHora}</td>
                        <td><span class="badge badge-primary">📡 ${det.lora_id || 'N/A'}</span></td>
                        <td><span class="badge badge-${badgeClass}">${statusIcon} ${qtdFlies}</span></td>
                        <td>${confMedia}%</td>
                        <td>${limiarConf}%</td>
                        <td>${numItens} bbox • ${ocupacao}% ocup</td>
                    </tr>
                `;
            }).join('');
        }
        
        // Carregar dados da API
        async function loadData() {
            try {
                const response = await fetch('/api/messages');
                const data = await response.json();
                
                updateStats(data);
                renderDetectionsTable(data.messages);
                renderDevices();
                
                // Atualizar graficos com dados reais se disponiveis
                if (data.messages && data.messages.length > 0) {
                    // Agrupar moscas detectadas por hora (ultimas 24h)
                    const hourlyDetections = {};
                    data.messages.forEach(msg => {
                        if (msg.timestamp) {
                            const hour = msg.timestamp.split(' ')[1].split(':')[0] + ':00';
                            const moscas = msg.deteccoes?.total || 0;
                            hourlyDetections[hour] = (hourlyDetections[hour] || 0) + moscas;
                        }
                    });
                    
                    // Atualizar grafico de deteccoes por hora
                    if (Object.keys(hourlyDetections).length > 0) {
                        const hours = Object.keys(hourlyDetections).sort();
                        const counts = hours.map(h => hourlyDetections[h]);
                        detectionsChart.data.labels = hours;
                        detectionsChart.data.datasets[0].data = counts;
                        detectionsChart.update('none');
                    }
                    
                    // Atualizar grafico de confianca media ao longo do tempo
                    const confidenceData = data.messages
                        .filter(m => m.deteccoes?.confianca_media)
                        .slice(-24)
                        .map((m, i) => ({
                            label: `#${i + 1}`,
                            value: (m.deteccoes.confianca_media * 100).toFixed(1)
                        }));
                    
                    if (confidenceData.length > 0) {
                        confidenceChart.data.labels = confidenceData.map(d => d.label);
                        confidenceChart.data.datasets[0].data = confidenceData.map(d => d.value);
                        confidenceChart.update('none');
                    }
                    
                    // Atualizar grafico de ocupacao (ultimas 10)
                    const lastOccupancy = data.messages.slice(-10).map(m => m.deteccoes?.ocupacao_pct || 0);
                    if (lastOccupancy.length > 0) {
                        occupancyChart.data.datasets[0].data = lastOccupancy;
                        occupancyChart.data.labels = lastOccupancy.map((_, i) => `Cap ${i + 1}`);
                        occupancyChart.update('none');
                    }
                    
                    // Atualizar grafico de tempo de inferencia (ultimas 10)
                    const lastInference = data.messages.slice(-10).map(m => m.tempo_inferencia_ms || 0);
                    if (lastInference.length > 0) {
                        inferenceChart.data.datasets[0].data = lastInference;
                        inferenceChart.data.labels = lastInference.map((_, i) => `Cap ${i + 1}`);
                        inferenceChart.update('none');
                    }
                }
                
            } catch (error) {
                console.error('Erro ao carregar dados:', error);
            }
        }
        
        // Inicializacao
        renderDevices();
        loadData();
        
        // Atualizar dados reais da API a cada 5 segundos
        setInterval(loadData, 5000);
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
        logger.error(f"[ERROR] Erro ao listar mensagens: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

def expand_lora_payload(compact_data):
    """
    Converte payload compacto LoRa para formato expandido interno
    
    Formato LoRa (compacto):
    {
        "dt": "20112025",        # data ddmmyyyy
        "hr": "14:30:45",        # hora
        "ti": 87,                # tempo inferência (ms)
        "m": 15,                 # total moscas
        "cm": 0.92,              # confiança média
        "cmin": 0.85,            # menor confiança
        "cmax": 0.95,            # maior confiança
        "op": 7.77,              # ocupação %
        "dg": {                  # diagnóstico
            "oe": false,         # ocupacao_excessiva
            "an": false          # anormal
        },
        "id": "LORA-001"         # id do dispositivo
    }
    
    Retorna formato expandido para processamento interno
    """
    # Detectar se é formato compacto (LoRa) ou expandido (legado)
    if "dt" in compact_data and "hr" in compact_data:
        # Formato compacto LoRa - expandir
        dt = compact_data.get("dt", "")  # ddmmyyyy
        hr = compact_data.get("hr", "00:00:00")
        
        # Converter data de ddmmyyyy para yyyy-mm-dd
        if len(dt) == 8:
            day = dt[0:2]
            month = dt[2:4]
            year = dt[4:8]
            timestamp = f"{year}-{month}-{day} {hr}"
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Expandir payload
        expanded = {
            "timestamp": timestamp,
            "tempo_inferencia_ms": compact_data.get("ti", 0),
            "deteccoes": {
                "total": compact_data.get("m", 0),
                "limiar_confianca": 0.5,  # Valor padrão (não vem no LoRa)
                "confianca_media": compact_data.get("cm", 0),
                "confianca_min": compact_data.get("cmin", 0),
                "confianca_max": compact_data.get("cmax", 0),
                "ocupacao_pct": compact_data.get("op", 0),
                "area_total_px": 0,  # Não disponível no formato compacto
                "itens": []  # Bounding boxes não são enviadas pelo LoRa
            },
            "diagnostico": {
                "ocupacao_excessiva": compact_data.get("dg", {}).get("oe", False),
                "anormal": compact_data.get("dg", {}).get("an", False)
            },
            "lora_id": compact_data.get("id", "UNKNOWN")
        }
        
        return expanded
    else:
        # Já está no formato expandido (compatibilidade legado)
        return compact_data

@app.route('/api/messages', methods=['POST'])
def receive_message():
    """
    Recebe detecções de moscas via POST e armazena
    
    FORMATO COMPACTO LORA (RECOMENDADO - mensagens curtas):
    {
        "dt": "20112025",        # data ddmmyyyy
        "hr": "14:30:45",        # hora
        "ti": 87,                # tempo inferência (ms)
        "m": 15,                 # total moscas
        "cm": 0.92,              # confiança média
        "cmin": 0.85,            # menor confiança
        "cmax": 0.95,            # maior confiança
        "op": 7.77,              # ocupação %
        "dg": {                  # diagnóstico
            "oe": false,         # ocupacao_excessiva (op > 20)
            "an": false          # anormal (op > 30 OU m > 50)
        },
        "id": "LORA-001"         # id do dispositivo
    }
    
    FORMATO EXPANDIDO (LEGADO - compatibilidade):
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
    """
    try:
        stats["total_messages"] += 1
        
        # Validar JSON
        raw_data = request.get_json()
        if not raw_data:
            logger.warning("[ERROR] JSON inválido ou ausente")
            return jsonify({"success": False, "error": "JSON inválido"}), 400
        
        # Expandir payload se necessário (LoRa -> formato interno)
        data = expand_lora_payload(raw_data)
        
        # Extrair dados do formato expandido
        client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        deteccoes = data.get('deteccoes', {})
        total_moscas = deteccoes.get('total', 0)
        lora_id = data.get('lora_id', 'Desconhecido')
        diagnostico = data.get('diagnostico', {})
        
        # Log da requisição
        status = "ANORMAL" if diagnostico.get('anormal') else "ALERTA" if diagnostico.get('ocupacao_excessiva') else "NORMAL"
        logger.info(f"[{status}] Detecção recebida: {total_moscas} moscas do dispositivo {lora_id}")
        
        # Adicionar metadata
        message_data = {
            **data,
            "source_ip": client_ip,
            "processed": True,
            "received_at": datetime.now().isoformat(),
            "original_format": "lora_compact" if "dt" in raw_data else "expanded"
        }
        
        # Armazenar mensagem
        messages_storage.append(message_data)
        logger.info(f"[STORAGE] Detecção armazenada (total: {len(messages_storage)})")
        
        return jsonify({
            "success": True,
            "message": f"Detecção recebida: {total_moscas} moscas",
            "stored": True,
            "message_id": len(messages_storage) - 1,
            "diagnostico": diagnostico,
            "format": "lora_compact" if "dt" in raw_data else "expanded"
        }), 200
        
    except Exception as e:
        stats["errors"] += 1
        logger.error(f"[ERROR] Erro ao processar detecção: {e}")
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
    print("TRAPEYES MESSAGE SERVER")
    print("="*60)
    print(f"Porta: {PORT}")
    print(f"Maximo de mensagens: {MAX_MESSAGES}")
    print()
    print("Endpoints:")
    print(f"  - GET  http://localhost:{PORT}/         (Dashboard)")
    print(f"  - POST http://localhost:{PORT}/api/messages (Receber mensagem)")
    print(f"  - GET  http://localhost:{PORT}/api/messages (Listar mensagens)")
    print(f"  - GET  http://localhost:{PORT}/api/stats (Estatisticas)")
    print()
    print("Servidor iniciado!")
    print("="*60)
    
    app.run(
        host='0.0.0.0',
        port=PORT,
        debug=os.getenv("DEBUG", "false").lower() == "true"
    )