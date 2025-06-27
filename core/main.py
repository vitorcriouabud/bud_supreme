import os
import sys
import asyncio
from core.main_controller import start_main_controller
from telegram_integration.sorte_telegram_bot import SorteTelegramBot
from utils.logger import Logger

# Configurar PYTHONPATH
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """
    Função principal da Sorte AI.
    Inicia todos os componentes necessários para operação autônoma.
    """
    logger = Logger("SorteMain")
    logger.info("🚀 Iniciando Sorte AI - Sistema Autônomo de Trading")
    
    try:
        # Verificar variáveis de ambiente essenciais
        required_vars = ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            logger.warning(f"Variáveis de ambiente ausentes: {missing_vars}")
            logger.info("Sistema iniciará em modo limitado")
        
        # Iniciar bot do Telegram em thread separada
        if os.getenv('TELEGRAM_BOT_TOKEN'):
            logger.info("Iniciando bot do Telegram...")
            telegram_bot = SorteTelegramBot()
            
            # Executar bot em loop assíncrono
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Iniciar controlador principal em thread separada
            import threading
            controller_thread = threading.Thread(target=start_main_controller)
            controller_thread.daemon = True
            controller_thread.start()
            
            # Executar bot do Telegram
            loop.run_until_complete(telegram_bot.start())
        else:
            logger.warning("Token do Telegram não configurado, iniciando apenas controlador principal")
            start_main_controller()
            
    except KeyboardInterrupt:
        logger.info("Interrupção pelo usuário, encerrando sistema...")
    except Exception as e:
        logger.error(f"Erro crítico na inicialização: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

