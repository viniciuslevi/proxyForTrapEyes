# 🔧 Setup Git e GitHub - TrapEyes

Guia passo a passo para subir o projeto no GitHub.

## 📋 Pré-requisitos

- Git instalado
- Conta no GitHub
- Repositório criado no GitHub (vazio)

## 🚀 Comandos

### 1. Inicializar Git (se ainda não foi feito)

```bash
cd /Users/H_CINTRA/Desktop/mosca/proxyForTrapEyes
git init
```

### 2. Configurar Git (primeira vez)

```bash
git config --global user.name "Seu Nome"
git config --global user.email "seu-email@exemplo.com"
```

### 3. Adicionar Arquivos

```bash
# Adicionar todos os arquivos (exceto os do .gitignore)
git add .

# Verificar o que será commitado
git status
```

### 4. Primeiro Commit

```bash
git commit -m "🦟 Initial commit: TrapEyes IoT Fly Detection System

- Dashboard profissional com visualizações em tempo real
- API REST completa para receber detecções IoT
- Suporte para dispositivos LoRa
- Diagnóstico automático (ocupação excessiva e situações anormais)
- 4 gráficos interativos (moscas, confiança, ocupação, inferência)
- Docker e Docker Compose prontos
- Documentação completa (README, QUICKSTART, DEPLOY)
- Scripts de teste incluídos"
```

### 5. Adicionar Repositório Remoto

```bash
# Substituir SEU-USUARIO e NOME-DO-REPO
git remote add origin https://github.com/SEU-USUARIO/NOME-DO-REPO.git

# Verificar
git remote -v
```

### 6. Push para o GitHub

```bash
# Primeira vez
git branch -M main
git push -u origin main

# Próximas vezes
git push
```

## 📝 Estrutura de Commits Sugerida

### Tipos de Commit

- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Atualização de documentação
- `style:` Formatação de código
- `refactor:` Refatoração de código
- `test:` Adição de testes
- `chore:` Tarefas de manutenção

### Exemplos

```bash
git commit -m "feat: adiciona validação de payload na API"
git commit -m "fix: corrige cálculo de ocupação média"
git commit -m "docs: atualiza README com exemplos Python"
git commit -m "refactor: melhora estrutura do código de gráficos"
```

## 🔄 Workflow Diário

```bash
# 1. Verificar status
git status

# 2. Adicionar mudanças
git add arquivo.py
# ou adicionar tudo
git add .

# 3. Commit
git commit -m "descrição das mudanças"

# 4. Push
git push
```

## 🌿 Trabalhando com Branches

```bash
# Criar nova branch
git checkout -b feature/nova-funcionalidade

# Fazer mudanças e commits
git add .
git commit -m "feat: implementa nova funcionalidade"

# Voltar para main
git checkout main

# Merge da branch
git merge feature/nova-funcionalidade

# Push
git push
```

## 📦 Criar Release

```bash
# Tag de versão
git tag -a v1.0.0 -m "Release v1.0.0: Primeira versão estável"

# Push da tag
git push origin v1.0.0
```

## 🔍 Comandos Úteis

```bash
# Ver histórico
git log --oneline --graph

# Ver mudanças não commitadas
git diff

# Desfazer mudanças (antes do add)
git checkout -- arquivo.py

# Desfazer add (antes do commit)
git reset HEAD arquivo.py

# Ver branches
git branch -a

# Atualizar do remoto
git pull
```

## 🛡️ .gitignore

Já configurado! Ignora:

- `venv/` - Ambiente virtual
- `__pycache__/` - Cache Python
- `*.pyc` - Bytecode Python
- `.env` - Variáveis de ambiente
- `*.log` - Logs
- `.DS_Store` - Arquivos do macOS

## 📋 Checklist antes do Push

- [ ] Código testado localmente
- [ ] Servidor inicia sem erros
- [ ] Dashboard acessível
- [ ] API responde corretamente
- [ ] README atualizado
- [ ] .gitignore configurado
- [ ] Sem senhas/tokens no código
- [ ] Commit message descritivo

## 🎯 Primeira Publicação

```bash
# 1. Inicializar
git init

# 2. Adicionar tudo
git add .

# 3. Commit inicial
git commit -m "🦟 Initial commit: TrapEyes IoT System"

# 4. Adicionar repositório GitHub
git remote add origin https://github.com/SEU-USUARIO/trapeyes.git

# 5. Push
git branch -M main
git push -u origin main
```

## 🌐 Criar Repositório no GitHub

1. Acesse https://github.com/new
2. Nome: `trapeyes`
3. Descrição: "🦟 Sistema IoT de Detecção de Moscas com IA e Dashboard em Tempo Real"
4. Público ou Privado (sua escolha)
5. **NÃO** inicialize com README, .gitignore ou license
6. Clique em "Create repository"
7. Siga os comandos acima

## 📄 README Badges (opcional)

Adicione no topo do README.md:

```markdown
![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)
```

## 🔐 SSH vs HTTPS

### HTTPS (mais simples)
```bash
git remote add origin https://github.com/usuario/repo.git
```

### SSH (mais seguro)
```bash
git remote add origin git@github.com:usuario/repo.git
```

---

**Pronto! Seu projeto está no GitHub! 🎉**

Compartilhe: `https://github.com/SEU-USUARIO/trapeyes`
