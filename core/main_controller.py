from bud_interpreter_service.interpreter import CommandInterpreter
from utils.logger import Logger
import time

def start_main_controller():
    """
    Inicia o controlador principal da Sorte AI.
    """
    logger = Logger("MainController")
    logger.info("🎯 Controlador principal da Sorte AI iniciado")
    
    try:
        # Inicializar interpretador de comandos
        interpreter = CommandInterpreter()
        logger.info("✅ Interpretador de comandos inicializado")
        
        # Verificar status do sistema
        status = interpreter.get_status()
        logger.info(f"📊 Status do sistema: {status['interpreter_status']}")
        
        # Loop principal de monitoramento
        logger.info("🔄 Iniciando loop de monitoramento...")
        
        while True:
            try:
                # Verificar saúde do sistema a cada 60 segundos
                time.sleep(60)
                
                # Verificar status dos componentes
                current_status = interpreter.get_status()
                
                if current_status['interpreter_status'] == 'active':
                    logger.info("✅ Sistema operacional - todos os componentes ativos")
                else:
                    logger.warning("⚠️ Possível problema detectado no sistema")
                
            except KeyboardInterrupt:
                logger.info("Interrupção detectada, encerrando controlador...")
                break
            except Exception as e:
                logger.error(f"Erro no loop de monitoramento: {e}")
                time.sleep(30)  # Aguardar antes de tentar novamente
                
    except Exception as e:
        logger.error(f"Erro crítico no controlador principal: {e}")
        raise

if __name__ == '__main__':
    start_main_controller()

