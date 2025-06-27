import asyncio
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from bud_interpreter_service.interpreter import CommandInterpreter
from utils.logger import Logger

class SorteTelegramBot:
    """
    Bot do Telegram para a Sorte AI.
    Permite controle e monitoramento via Telegram.
    """
    
    def __init__(self):
        self.logger = Logger("SorteTelegramBot")
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.interpreter = CommandInterpreter()
        
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN não configurado")
        
        if not self.chat_id:
            raise ValueError("TELEGRAM_CHAT_ID não configurado")
        
        # Criar aplicação do bot
        self.application = Application.builder().token(self.token).build()
        
        # Registrar handlers
        self._register_handlers()
        
        self.logger.info("Bot do Telegram inicializado")
    
    def _register_handlers(self):
        """Registra os handlers de comandos e mensagens."""
        
        # Comandos específicos
        self.application.add_handler(CommandHandler("start", self._start_command))
        self.application.add_handler(CommandHandler("status", self._status_command))
        self.application.add_handler(CommandHandler("help", self._help_command))
        self.application.add_handler(CommandHandler("backup", self._backup_command))
        
        # Handler para mensagens de texto (comandos em linguagem natural)
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_natural_command)
        )
    
    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para o comando /start."""
        welcome_message = """
🤖 **Sorte AI - Sistema Autônomo Ativado**

Olá! Eu sou a Sorte, sua IA de trading autônoma.

**Comandos disponíveis:**
• `/status` - Ver status do sistema
• `/backup` - Criar backup manual
• `/help` - Ver ajuda completa

**Comandos em linguagem natural:**
• "seja mais agressiva"
• "reduza o risco"
• "otimize a performance"
• "criar backup"
• "status do sistema"

Estou pronta para operar! 🚀
        """
        
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
        self.logger.info(f"Comando /start executado por {update.effective_user.id}")
    
    async def _status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para o comando /status."""
        try:
            # Obter status do interpretador
            interpreter_status = self.interpreter.get_status()
            
            status_message = f"""
📊 **Status da Sorte AI**

🔧 **Componentes:**
• Interpretador: {interpreter_status['interpreter_status']}
• Editor: {interpreter_status['editor_status']}
• Guardian: {interpreter_status['guardian_status']}

🧠 **Modelo de IA:**
• Local disponível: {interpreter_status['llm_bridge_status']['local_model_available']}
• Fallback ativo: {interpreter_status['llm_bridge_status']['fallback_enabled']}

📁 **Categorias suportadas:**
{chr(10).join([f"• {cat}" for cat in interpreter_status['supported_categories']])}

✅ **Sistema operacional e pronto para comandos!**
            """
            
            await update.message.reply_text(status_message, parse_mode='Markdown')
            self.logger.info("Status enviado via Telegram")
            
        except Exception as e:
            error_message = f"❌ Erro ao obter status: {str(e)}"
            await update.message.reply_text(error_message)
            self.logger.error(f"Erro no comando status: {e}")
    
    async def _help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para o comando /help."""
        help_message = """
📚 **Ajuda - Sorte AI**

**Comandos do Bot:**
• `/start` - Inicializar bot
• `/status` - Ver status do sistema
• `/backup` - Criar backup manual
• `/help` - Esta ajuda

**Comandos em Linguagem Natural:**

🎯 **Estratégia:**
• "seja mais agressiva"
• "seja mais conservadora"
• "modifique a estratégia"

⚠️ **Gestão de Risco:**
• "reduza o risco"
• "aumente o risco"
• "ajuste o stop loss"

⚡ **Performance:**
• "otimize a performance"
• "melhore a velocidade"
• "otimize o algoritmo"

🔧 **Sistema:**
• "criar backup"
• "status do sistema"
• "reiniciar sistema"

**Exemplo de uso:**
Envie: "seja mais agressiva com tendência de alta"
Resultado: Sorte modificará automaticamente os parâmetros de trading

🚀 **Estou sempre aprendendo e evoluindo!**
        """
        
        await update.message.reply_text(help_message, parse_mode='Markdown')
        self.logger.info("Ajuda enviada via Telegram")
    
    async def _backup_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para o comando /backup."""
        try:
            await update.message.reply_text("🔄 Criando backup manual...")
            
            # Executar comando de backup
            result = self.interpreter.execute_command("criar backup manual")
            
            if result['success']:
                success_message = f"""
✅ **Backup criado com sucesso!**

📁 Arquivo: {result.get('backup_created', 'backup_manual')}
🕒 Timestamp: {result.get('timestamp', 'agora')}
🔧 Modelo usado: {result.get('model_used', 'template')}

Backup seguro e pronto para restauração se necessário.
                """
                await update.message.reply_text(success_message, parse_mode='Markdown')
            else:
                error_message = f"❌ Erro ao criar backup: {result.get('error', 'Erro desconhecido')}"
                await update.message.reply_text(error_message)
            
        except Exception as e:
            error_message = f"❌ Erro no comando backup: {str(e)}"
            await update.message.reply_text(error_message)
            self.logger.error(f"Erro no comando backup: {e}")
    
    async def _handle_natural_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler para comandos em linguagem natural."""
        try:
            # Verificar se a mensagem é do chat autorizado
            if str(update.effective_chat.id) != self.chat_id:
                await update.message.reply_text("❌ Chat não autorizado")
                return
            
            command = update.message.text
            self.logger.info(f"Comando recebido: {command}")
            
            # Enviar confirmação de recebimento
            await update.message.reply_text(f"🔄 Processando: '{command}'...")
            
            # Executar comando
            result = self.interpreter.execute_command(command)
            
            if result['success']:
                success_message = f"""
✅ **Comando executado com sucesso!**

📝 **Comando:** {command}
📂 **Categoria:** {result.get('category', 'N/A')}
📁 **Arquivo modificado:** {result.get('target_file', 'N/A')}
🧠 **Modelo usado:** {result.get('model_used', 'N/A')}
🧪 **Testes:** {'✅ Passou' if result.get('tests_passed') else '⚠️ Verificar'}

💡 **Explicação:** {result.get('explanation', 'Comando executado')}

🚀 **Sistema atualizado e operacional!**
                """
                await update.message.reply_text(success_message, parse_mode='Markdown')
                
            else:
                error_message = f"""
❌ **Erro na execução do comando**

📝 **Comando:** {command}
🚫 **Erro:** {result.get('error', 'Erro desconhecido')}

Tente reformular o comando ou use /help para ver exemplos.
                """
                await update.message.reply_text(error_message, parse_mode='Markdown')
            
        except Exception as e:
            error_message = f"❌ Erro interno: {str(e)}"
            await update.message.reply_text(error_message)
            self.logger.error(f"Erro no processamento de comando: {e}")
    
    async def send_alert(self, message: str, priority: str = "info"):
        """
        Envia alerta para o chat configurado.
        """
        try:
            # Emojis baseados na prioridade
            emoji_map = {
                "critical": "🚨",
                "warning": "⚠️",
                "info": "ℹ️",
                "success": "✅"
            }
            
            emoji = emoji_map.get(priority, "ℹ️")
            formatted_message = f"{emoji} **Sorte AI Alert**\n\n{message}"
            
            await self.application.bot.send_message(
                chat_id=self.chat_id,
                text=formatted_message,
                parse_mode='Markdown'
            )
            
            self.logger.info(f"Alerta enviado: {priority}")
            
        except Exception as e:
            self.logger.error(f"Erro ao enviar alerta: {e}")
    
    async def send_startup_message(self):
        """
        Envia mensagem de inicialização.
        """
        startup_message = """
🚀 **Sorte AI Iniciada com Sucesso!**

✅ Sistema autônomo ativo
✅ Interpretador de comandos operacional
✅ Modelo de IA independente configurado
✅ Sistema de backup ativo
✅ Monitoramento em tempo real

**Agora eu sou 100% autônoma, Vitor!**

Pronta para receber comandos e operar de forma independente.
Envie /help para ver todos os comandos disponíveis.

🎯 **Objetivo:** Maximizar lucros com autonomia total
🛡️ **Segurança:** Backups automáticos e validação de código
🧠 **Inteligência:** Modelo local independente da OpenAI

**Vamos começar a gerar resultados! 💰**
        """
        
        try:
            await self.application.bot.send_message(
                chat_id=self.chat_id,
                text=startup_message,
                parse_mode='Markdown'
            )
            self.logger.info("Mensagem de inicialização enviada")
        except Exception as e:
            self.logger.error(f"Erro ao enviar mensagem de inicialização: {e}")
    
    async def start(self):
        """
        Inicia o bot do Telegram.
        """
        try:
            self.logger.info("Iniciando bot do Telegram...")
            
            # Inicializar aplicação
            await self.application.initialize()
            await self.application.start()
            
            # Enviar mensagem de inicialização
            await self.send_startup_message()
            
            # Iniciar polling
            await self.application.updater.start_polling()
            
            self.logger.info("Bot do Telegram ativo e aguardando comandos")
            
            # Manter o bot rodando
            await self.application.updater.idle()
            
        except Exception as e:
            self.logger.error(f"Erro ao iniciar bot: {e}")
            raise
        finally:
            # Cleanup
            await self.application.stop()
            await self.application.shutdown()
    
    def stop(self):
        """
        Para o bot do Telegram.
        """
        try:
            self.logger.info("Parando bot do Telegram...")
            # O cleanup será feito no finally do método start()
        except Exception as e:
            self.logger.error(f"Erro ao parar bot: {e}")

