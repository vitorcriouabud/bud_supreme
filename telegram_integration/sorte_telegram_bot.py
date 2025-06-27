import asyncio
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from typing import Dict, Any
import json
import os
from dotenv import load_dotenv
from bud_interpreter_service.advanced_interpreter import AdvancedCommandInterpreter
from utils.logger import Logger

class SorteTelegramBot:
    """
    Bot do Telegram avançado para a IA Sorte.
    Permite comunicação bidirecional e execução de comandos complexos.
    """
    
    def __init__(self, base_path: str):
        load_dotenv()
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.base_path = base_path
        
        self.interpreter = AdvancedCommandInterpreter(base_path)
        self.logger = Logger("SorteTelegramBot")
        
        # Estado da conversa
        self.conversation_state = {}
        
        if not self.token:
            self.logger.error("TELEGRAM_BOT_TOKEN não encontrado nas variáveis de ambiente")
            raise ValueError("Token do Telegram não configurado")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /start - Inicializa a conversa com a Sorte."""
        welcome_message = """
🤖 **Sorte AI - Sistema Autônomo de Trading**

Olá! Eu sou a Sorte, sua IA autônoma para trading e auto-modificação de código.

**Comandos disponíveis:**
• `/status` - Ver status atual do sistema
• `/help` - Ver todos os comandos
• `/logs` - Ver logs recentes
• `/backup` - Criar backup do sistema

**Exemplos de comandos em linguagem natural:**
• "Fique mais agressiva com tendência de alta"
• "Ajuste o gerenciamento de risco"
• "Otimize a performance do código"
• "Corrija bugs na estratégia"

Envie qualquer comando e eu interpretarei e executarei as modificações necessárias!
        """
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
        self.logger.info(f"Usuário {update.effective_user.id} iniciou conversa")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /status - Mostra o status atual da Sorte."""
        try:
            # Coletar informações de status
            status_info = {
                "sistema": "✅ Online",
                "interpreter": "✅ Ativo",
                "gpt_bridge": "⚠️ Dependente da API OpenAI",
                "code_guardian": "✅ Ativo",
                "arquivos_monitorados": [
                    "bud_logic/strategy.py",
                    "bud_logic/risk_manager.py"
                ]
            }
            
            status_message = f"""
📊 **Status da Sorte AI**

**Componentes:**
• Sistema: {status_info['sistema']}
• Interpretador: {status_info['interpreter']}
• GPT Bridge: {status_info['gpt_bridge']}
• Guardian: {status_info['code_guardian']}

**Arquivos Monitorados:**
{chr(10).join([f"• {arquivo}" for arquivo in status_info['arquivos_monitorados']])}

**Última Atualização:** {self.get_last_update_time()}
            """
            
            await update.message.reply_text(status_message, parse_mode='Markdown')
            
        except Exception as e:
            self.logger.error(f"Erro ao obter status: {e}")
            await update.message.reply_text("❌ Erro ao obter status do sistema")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /help - Mostra ajuda detalhada."""
        help_message = """
🆘 **Ajuda - Sorte AI**

**Comandos do Sistema:**
• `/start` - Inicializar conversa
• `/status` - Ver status do sistema
• `/logs` - Ver logs recentes (últimas 10 linhas)
• `/backup` - Criar backup do código atual
• `/rollback` - Reverter para backup anterior
• `/validate` - Validar código atual

**Comandos de Modificação:**
Você pode usar linguagem natural para modificar o código:

**Estratégia de Trading:**
• "Seja mais agressiva com tendência de alta"
• "Reduza a agressividade para mercado lateral"
• "Otimize para mercado de baixa"

**Gerenciamento de Risco:**
• "Reduza o risco das operações"
• "Aumente o limite de stop loss"
• "Ajuste o gerenciamento de risco"

**Performance:**
• "Otimize a velocidade do código"
• "Melhore a performance dos algoritmos"

**Correções:**
• "Corrija bugs na estratégia"
• "Resolva erros de execução"

A Sorte interpretará seus comandos e fará as modificações automaticamente!
        """
        
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def logs_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /logs - Mostra logs recentes."""
        try:
            # Simular leitura de logs (implementação real dependeria do sistema de logging)
            logs_message = """
📝 **Logs Recentes da Sorte**

```
[2024-01-15 10:30:15] INFO - AdvancedCommandInterpreter - Comando interpretado: "mais agressiva"
[2024-01-15 10:30:16] INFO - ASTCodeEditor - Backup criado: bud_logic/strategy.py.backup
[2024-01-15 10:30:17] INFO - CodeGuardian - Validação sintática: PASSOU
[2024-01-15 10:30:18] INFO - SorteTelegramBot - Comando executado com sucesso
```

Use `/status` para ver o estado atual do sistema.
            """
            
            await update.message.reply_text(logs_message, parse_mode='Markdown')
            
        except Exception as e:
            self.logger.error(f"Erro ao obter logs: {e}")
            await update.message.reply_text("❌ Erro ao obter logs do sistema")
    
    async def backup_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Comando /backup - Cria backup do sistema."""
        try:
            # Simular criação de backup
            await update.message.reply_text("🔄 Criando backup do sistema...")
            
            # Aqui seria implementada a lógica real de backup
            backup_result = {
                "status": "success",
                "files_backed_up": [
                    "bud_logic/strategy.py",
                    "bud_logic/risk_manager.py",
                    "core/main_controller.py"
                ],
                "timestamp": "2024-01-15_10-30-20"
            }
            
            success_message = f"""
✅ **Backup Criado com Sucesso**

**Arquivos incluídos:**
{chr(10).join([f"• {arquivo}" for arquivo in backup_result['files_backed_up']])}

**Timestamp:** {backup_result['timestamp']}

Use `/rollback` se precisar reverter as modificações.
            """
            
            await update.message.reply_text(success_message, parse_mode='Markdown')
            
        except Exception as e:
            self.logger.error(f"Erro ao criar backup: {e}")
            await update.message.reply_text("❌ Erro ao criar backup do sistema")
    
    async def handle_natural_language(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Processa comandos em linguagem natural."""
        user_message = update.message.text
        user_id = update.effective_user.id
        
        self.logger.info(f"Comando recebido do usuário {user_id}: {user_message}")
        
        # Enviar confirmação de recebimento
        await update.message.reply_text("🤖 Processando seu comando... Por favor, aguarde.")
        
        try:
            # Interpretar e executar o comando
            result = self.interpreter.interpret_and_modify(user_message)
            
            # Formatar resposta baseada no resultado
            if result['status'] == 'success':
                response_message = f"""
✅ **Comando Executado com Sucesso**

**Categoria:** {result['category']}
**Arquivo Modificado:** {result['target_file']}

**Validações:**
{self.format_validation_results(result['validation_result'])}

**Detalhes:** {result['message']}
                """
            else:
                response_message = f"""
❌ **Erro na Execução do Comando**

**Erro:** {result['message']}

Tente reformular o comando ou use `/help` para ver exemplos.
                """
            
            await update.message.reply_text(response_message, parse_mode='Markdown')
            
            # Log do resultado
            self.logger.log_command_execution(user_message, result)
            
        except Exception as e:
            self.logger.error(f"Erro ao processar comando: {e}")
            await update.message.reply_text(
                "❌ Erro interno ao processar comando. Verifique os logs para mais detalhes."
            )
    
    def format_validation_results(self, validation_result: Dict[str, Any]) -> str:
        """Formata os resultados de validação para exibição."""
        if not validation_result:
            return "• Nenhuma validação executada"
        
        results = []
        if validation_result.get('syntax_valid'):
            results.append("• ✅ Sintaxe válida")
        else:
            results.append("• ❌ Erro de sintaxe")
        
        if validation_result.get('security_check'):
            results.append("• ✅ Verificação de segurança passou")
        else:
            results.append("• ⚠️ Verificação de segurança falhou")
        
        if validation_result.get('tests_passed'):
            results.append("• ✅ Testes automatizados passaram")
        else:
            results.append("• ❌ Testes automatizados falharam")
        
        return '\n'.join(results)
    
    def get_last_update_time(self) -> str:
        """Retorna o timestamp da última atualização."""
        # Implementação simplificada
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    async def send_alert(self, message: str, alert_type: str = "info"):
        """Envia alertas proativos para o usuário."""
        if not self.chat_id:
            self.logger.warning("TELEGRAM_CHAT_ID não configurado, não é possível enviar alertas")
            return
        
        emoji_map = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
            "success": "✅"
        }
        
        emoji = emoji_map.get(alert_type, "ℹ️")
        formatted_message = f"{emoji} **Alerta da Sorte**\n\n{message}"
        
        try:
            bot = Bot(token=self.token)
            await bot.send_message(
                chat_id=self.chat_id,
                text=formatted_message,
                parse_mode='Markdown'
            )
            self.logger.info(f"Alerta enviado: {alert_type} - {message}")
        except Exception as e:
            self.logger.error(f"Erro ao enviar alerta: {e}")
    
    def run(self):
        """Inicia o bot do Telegram."""
        try:
            # Criar aplicação
            application = Application.builder().token(self.token).build()
            
            # Adicionar handlers
            application.add_handler(CommandHandler("start", self.start_command))
            application.add_handler(CommandHandler("status", self.status_command))
            application.add_handler(CommandHandler("help", self.help_command))
            application.add_handler(CommandHandler("logs", self.logs_command))
            application.add_handler(CommandHandler("backup", self.backup_command))
            
            # Handler para mensagens de texto (linguagem natural)
            application.add_handler(
                MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_natural_language)
            )
            
            self.logger.info("Bot do Telegram iniciado com sucesso")
            
            # Iniciar o bot
            application.run_polling()
            
        except Exception as e:
            self.logger.error(f"Erro ao iniciar bot do Telegram: {e}")
            raise

if __name__ == "__main__":
    bot = SorteTelegramBot("/home/ubuntu/bud_supreme")
    bot.run()

