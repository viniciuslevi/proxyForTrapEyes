# 🚀 Deploy TrapEyes na AWS EC2 (HTTP)

Deploy simples usando AWS EC2 com HTTP puro (sem HTTPS).

## ✨ Características

- 📄 **Arquivo único** - `main.tf` com tudo incluído
- 🖥️ **AWS EC2** - Máquina virtual t2.micro (Free Tier)
- 🌐 **HTTP puro** - Sem SSL/HTTPS
- 💰 **Custo** - ~$5-10/mês (ou grátis no Free Tier)
- 🔑 **SSH** - Acesso completo à máquina

## 📋 Pré-requisitos

1. **AWS CLI** configurado
   ```bash
   aws configure
   ```

2. **Terraform** >= 1.0
   ```bash
   terraform --version
   ```

3. **Chave SSH** (será criada se não existir)
   ```bash
   ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa
   ```

## 🚀 Deploy em 4 Passos

### 1. Criar infraestrutura AWS

```bash
cd terraform
terraform init
terraform apply
```

Isso criará:
- ✅ EC2 t2.micro (Free Tier)
- ✅ Security Group (portas 5000 e 22)
- ✅ Elastic IP (IP fixo)
- ✅ Key Pair (chave SSH)

### 2. Aguardar EC2 iniciar (~2 minutos)

### 3. Copiar código da aplicação

```bash
# Do diretório terraform/
scp -i ~/.ssh/id_rsa ../app.py ubuntu@$(terraform output -raw instance_public_ip):/opt/trapeyes/
```

### 4. Iniciar aplicação

```bash
ssh -i ~/.ssh/id_rsa ubuntu@$(terraform output -raw instance_public_ip) "cd /opt/trapeyes && docker-compose up -d --build"
```

### 5. Acessar aplicação

```bash
terraform output app_url
# Exemplo: http://3.80.123.45:5000
```

## 📊 Comandos Úteis

### Ver URL da aplicação
```bash
terraform output app_url
```

### Conectar via SSH
```bash
ssh -i ~/.ssh/id_rsa ubuntu@$(terraform output -raw instance_public_ip)
```

### Ver logs da aplicação
```bash
ssh ubuntu@$(terraform output -raw instance_public_ip) "cd /opt/trapeyes && docker-compose logs -f"
```

### Reiniciar aplicação
```bash
ssh ubuntu@$(terraform output -raw instance_public_ip) "cd /opt/trapeyes && docker-compose restart"
```

### Atualizar código (após mudanças)
```bash
# Copiar novo código
scp -i ~/.ssh/id_rsa ../app.py ubuntu@$(terraform output -raw instance_public_ip):/opt/trapeyes/

# Rebuild e restart
ssh ubuntu@$(terraform output -raw instance_public_ip) "cd /opt/trapeyes && docker-compose up -d --build"
```

### Ver status dos containers
```bash
ssh ubuntu@$(terraform output -raw instance_public_ip) "docker ps"
```

## 🔧 Personalização

Crie um arquivo `terraform.tfvars`:

```hcl
aws_region     = "us-east-1"
project_name   = "meu-trapeyes"
port           = 5000
max_messages   = 1000
instance_type  = "t2.micro"
allowed_cidr   = "0.0.0.0/0"  # Trocar para seu IP para mais segurança
ssh_key_path   = "~/.ssh/id_rsa.pub"
```

## 🔒 Segurança

### Restringir acesso por IP

Para maior segurança, limite o acesso apenas ao seu IP:

```hcl
# terraform.tfvars
allowed_cidr = "SEU.IP.AQUI.0/32"
```

Descubra seu IP:
```bash
curl ifconfig.me
```

### Desabilitar SSH

Se não precisar de SSH, comente no `main.tf`:

```hcl
# Comentar este bloco:
# ingress {
#   from_port   = 22
#   to_port     = 22
#   ...
# }
```

## 🔄 Atualizações

### Atualizar aplicação
```bash
# 1. Fazer mudanças no app.py local
# 2. Copiar para EC2
scp -i ~/.ssh/id_rsa ../app.py ubuntu@$(terraform output -raw instance_public_ip):/opt/trapeyes/
# 3. Rebuild
ssh ubuntu@$(terraform output -raw instance_public_ip) "cd /opt/trapeyes && docker-compose up -d --build"
```

### Atualizar infraestrutura
```bash
# Modificar main.tf ou terraform.tfvars
terraform plan
terraform apply
```

## �� Remover tudo

```bash
terraform destroy
```

⚠️ **Atenção:** Isso removerá TODOS os recursos da AWS!

## 💰 Custos Estimados

| Recurso | Especificação | Custo/mês |
|---------|---------------|-----------|
| EC2 t2.micro | Free Tier (750h/mês) | $0 - $10 |
| Elastic IP | IP fixo | $0 (enquanto anexado) |
| Storage | 8GB EBS | $0.80 |
| Transfer | Outbound | Variável |
| **Total** | | **$1-10/mês** |

*Free Tier: 12 meses grátis para novos clientes AWS*

## 🛡️ Recursos Criados

- ✅ EC2 Instance (t2.micro Ubuntu 22.04)
- ✅ Security Group (HTTP 5000, SSH 22)
- ✅ Elastic IP (IP público fixo)
- ✅ Key Pair (chave SSH)
- ✅ Docker + Docker Compose instalados
- ✅ Aplicação configurada em /opt/trapeyes

## 🆘 Troubleshooting

### Erro: "Connection refused"
```bash
# Verificar se Docker está rodando
ssh ubuntu@$(terraform output -raw instance_public_ip) "sudo systemctl status docker"

# Verificar logs
ssh ubuntu@$(terraform output -raw instance_public_ip) "cd /opt/trapeyes && docker-compose logs"
```

### Erro: "Permission denied (publickey)"
```bash
# Verificar se a chave existe
ls -la ~/.ssh/id_rsa

# Gerar nova chave
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa

# Recriar infraestrutura
terraform destroy
terraform apply
```

### EC2 não responde
```bash
# Verificar status na AWS
aws ec2 describe-instance-status --instance-ids $(terraform output -raw instance_id)

# Ver logs de inicialização
aws ec2 get-console-output --instance-id $(terraform output -raw instance_id)
```

### Porta 5000 bloqueada
```bash
# Verificar Security Group
aws ec2 describe-security-groups --group-ids $(terraform show -json | jq -r '.values.root_module.resources[] | select(.type=="aws_security_group") | .values.id')
```

## 📁 Estrutura na EC2

```
/opt/trapeyes/
├── app.py              # Código da aplicação
├── requirements.txt    # Dependências Python
├── Dockerfile         # Imagem Docker
├── docker-compose.yml # Orquestração
└── .env              # Variáveis de ambiente
```

## 📚 Recursos

- [AWS EC2](https://aws.amazon.com/ec2/)
- [AWS Free Tier](https://aws.amazon.com/free/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)

## 🎯 Próximos Passos

Após o deploy:
1. ✅ Teste o endpoint: `curl http://SEU_IP:5000/health`
2. ✅ Acesse o dashboard: `http://SEU_IP:5000`
3. ✅ Configure seus dispositivos IoT com a URL HTTP
4. ✅ Monitore os logs via SSH

---

**Desenvolvido com ❤️ para TrapEyes**
