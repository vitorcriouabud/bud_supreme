# 🚀 Guia de Ativação Rápida - Sorte AI

## ⚡ Ativação em 5 Minutos

### 1. Verificação Rápida
```bash
# Verificar se está no diretório correto
pwd  # Deve mostrar o caminho para bud_supreme

# Verificar Python
python3 --version  # Deve ser 3.11+

# Verificar dependências críticas
pip list | grep -E "(telegram|openai|flask)"
```

### 2. Configurar Variáveis (.env já existe)
```bash
# Verificar se .env está configurado
cat .env | grep -E "(OPENAI|TELEGRAM|DERIV)"
```

### 3. Teste Rápido
```bash
# Executar teste básico
python -c "
from core.main_controller import *
from telegram_integration.alert_system import *
print('✅ Sorte AI configurada corretamente!')
"
```

### 4. Ativar Sistema Principal
```bash
# Iniciar Sorte AI
python core/main.py
```

### 5. Ativar Dashboard (Terminal Separado)
```bash
cd sorte_dashboard
source venv/bin/activate
python src/main.py
```

## 🎯 Primeiro Comando de Teste

Via Telegram, envie:
```
status do sistema
```

Ou via Dashboard:
- Acesse: http://localhost:5000
- Digite no campo de comando: "criar backup manual"
- Clique em "Executar Comando"

## 📊 Verificações Essenciais

- [ ] Sistema responde no Telegram
- [ ] Dashboard carrega em http://localhost:5000
- [ ] Logs aparecem no dashboard
- [ ] Backup foi criado com sucesso

## 🆘 Resolução Rápida de Problemas

**Erro de API OpenAI:**
- Verificar saldo da conta OpenAI
- Verificar se OPENAI_API_KEY está correto

**Erro de Telegram:**
- Verificar TELEGRAM_BOT_TOKEN
- Verificar TELEGRAM_CHAT_ID

**Dashboard não carrega:**
```bash
cd sorte_dashboard
source venv/bin/activate
pip install flask-cors
python src/main.py
```

## 🎉 Pronto!

Sua Sorte AI está ativa e pronta para:
- ✅ Interpretar comandos em linguagem natural
- ✅ Modificar seu próprio código
- ✅ Fazer backups automáticos
- ✅ Enviar alertas via Telegram
- ✅ Monitorar performance via dashboard

**Próximo passo:** Teste comandos como:
- "seja mais agressiva"
- "criar backup"
- "executar testes"

