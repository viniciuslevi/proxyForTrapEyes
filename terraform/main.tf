# ========================================
# TrapEyes - Deploy AWS EC2 (HTTP)
# Arquivo único e completo
# ========================================

terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# ========================================
# Variáveis
# ========================================

variable "aws_region" {
  description = "Região AWS"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Nome do projeto"
  type        = string
  default     = "trapeyes"
}

variable "port" {
  description = "Porta da aplicação"
  type        = number
  default     = 5000
}

variable "max_messages" {
  description = "Máximo de mensagens em memória"
  type        = number
  default     = 1000
}

variable "instance_type" {
  description = "Tipo de instância EC2"
  type        = string
  default     = "t2.micro" # Free tier eligible
}

variable "allowed_cidr" {
  description = "CIDR permitido para acessar o servidor (0.0.0.0/0 = público)"
  type        = string
  default     = "0.0.0.0/0"
}

variable "ssh_key_path" {
  description = "Caminho para chave SSH pública"
  type        = string
  default     = "~/.ssh/id_rsa.pub"
}

# ========================================
# Provider
# ========================================

provider "aws" {
  region = var.aws_region
}

# ========================================
# Data Sources
# ========================================

# Pegar AMI mais recente do Ubuntu
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# ========================================
# VPC e Networking
# ========================================

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.project_name}-vpc"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.project_name}-igw"
  }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone       = "${var.aws_region}a"

  tags = {
    Name = "${var.project_name}-public-subnet"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "${var.project_name}-public-rt"
  }
}

resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}

# ========================================
# Security Group
# ========================================

resource "aws_security_group" "trapeyes" {
  name        = "${var.project_name}-sg"
  description = "Security group para TrapEyes EC2"
  vpc_id      = aws_vpc.main.id

  # Porta da aplicacao (HTTP)
  ingress {
    from_port   = var.port
    to_port     = var.port
    protocol    = "tcp"
    cidr_blocks = [var.allowed_cidr]
    description = "HTTP application port"
  }

  # SSH (opcional, para debug)
  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.allowed_cidr]
    description = "SSH access"
  }

  # Saída irrestrita
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound"
  }

  tags = {
    Name        = "${var.project_name}-sg"
    Environment = "production"
  }
}

# ========================================
# Key Pair
# ========================================

resource "aws_key_pair" "trapeyes" {
  count = fileexists(pathexpand(var.ssh_key_path)) ? 1 : 0
  
  key_name   = "${var.project_name}-key"
  public_key = file(pathexpand(var.ssh_key_path))

  tags = {
    Name = "${var.project_name}-key"
  }
}

# ========================================
# EC2 Instance
# ========================================

resource "aws_instance" "trapeyes" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  key_name      = length(aws_key_pair.trapeyes) > 0 ? aws_key_pair.trapeyes[0].key_name : null
  subnet_id     = aws_subnet.public.id

  vpc_security_group_ids = [aws_security_group.trapeyes.id]

  user_data = <<-EOF
              #!/bin/bash
              set -e
              
              # Atualizar sistema
              apt-get update
              apt-get install -y docker.io docker-compose git curl
              
              # Iniciar Docker
              systemctl start docker
              systemctl enable docker
              
              # Adicionar ubuntu ao grupo docker
              usermod -aG docker ubuntu
              
              # Criar diretório da aplicação
              mkdir -p /opt/trapeyes
              cd /opt/trapeyes
              
              # Criar app.py (código da aplicação será copiado depois via SCP)
              # Por enquanto, criar placeholder
              touch app.py
              
              # Criar requirements.txt
              cat > requirements.txt <<'REQUIREMENTS'
Flask==3.0.0
flask-cors==4.0.0
REQUIREMENTS
              
              # Criar .env
              cat > .env <<'ENVFILE'
PORT=${var.port}
MAX_MESSAGES=${var.max_messages}
DEBUG=false
ENVFILE
              
              # Criar Dockerfile
              cat > Dockerfile <<'DOCKERFILE'
FROM python:3.11-slim

WORKDIR /app

RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

USER appuser

EXPOSE ${var.port}

CMD ["python", "app.py"]
DOCKERFILE
              
              # Criar docker-compose.yml
              cat > docker-compose.yml <<'COMPOSE'
version: '3.8'

services:
  trapeyes:
    build: .
    container_name: trapeyes-server
    ports:
      - "${var.port}:${var.port}"
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:${var.port}/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
COMPOSE
              
              # Log de conclusão
              echo "TrapEyes preparado! Aguardando código app.py..." > /var/log/trapeyes-install.log
              date >> /var/log/trapeyes-install.log
              EOF

  user_data_replace_on_change = true

  tags = {
    Name        = "${var.project_name}-server"
    Environment = "production"
  }
}

# ========================================
# Elastic IP
# ========================================

resource "aws_eip" "trapeyes" {
  instance = aws_instance.trapeyes.id
  domain   = "vpc"

  tags = {
    Name = "${var.project_name}-eip"
  }
}

# ========================================
# Outputs
# ========================================

output "instance_id" {
  description = "ID da instância EC2"
  value       = aws_instance.trapeyes.id
}

output "instance_public_ip" {
  description = "IP público da instância"
  value       = aws_eip.trapeyes.public_ip
}

output "app_url" {
  description = "URL da aplicação (HTTP)"
  value       = "http://${aws_eip.trapeyes.public_ip}:${var.port}"
}

output "dashboard_url" {
  description = "URL do dashboard"
  value       = "http://${aws_eip.trapeyes.public_ip}:${var.port}/"
}

output "ssh_command" {
  description = "Comando para conectar via SSH"
  value       = "ssh -i ~/.ssh/id_rsa ubuntu@${aws_eip.trapeyes.public_ip}"
}

output "deploy_command" {
  description = "Comando para fazer deploy do app.py"
  value       = "scp -i ~/.ssh/id_rsa ../app.py ubuntu@${aws_eip.trapeyes.public_ip}:/opt/trapeyes/ && ssh -i ~/.ssh/id_rsa ubuntu@${aws_eip.trapeyes.public_ip} 'cd /opt/trapeyes && docker-compose up -d --build'"
}

# ========================================
# Instruções de Deploy
# ========================================

# DEPLOY EM 4 PASSOS:
#
# 1. Gerar chave SSH (se não tiver):
#    ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa
#
# 2. Inicializar e aplicar Terraform:
#    terraform init
#    terraform apply
#
# 3. Aguardar ~2 minutos para EC2 iniciar, então copiar código:
#    scp -i ~/.ssh/id_rsa ../app.py ubuntu@$(terraform output -raw instance_public_ip):/opt/trapeyes/
#
# 4. Iniciar aplicação na EC2:
#    ssh -i ~/.ssh/id_rsa ubuntu@$(terraform output -raw instance_public_ip) "cd /opt/trapeyes && docker-compose up -d --build"
#
# 5. Acessar:
#    terraform output app_url
#
# COMANDOS ÚTEIS:
#
# - Ver logs:
#   ssh ubuntu@$(terraform output -raw instance_public_ip) "cd /opt/trapeyes && docker-compose logs -f"
#
# - Reiniciar app:
#   ssh ubuntu@$(terraform output -raw instance_public_ip) "cd /opt/trapeyes && docker-compose restart"
#
# - Atualizar app após mudanças:
#   terraform output -raw deploy_command | bash
