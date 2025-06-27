from bud_interpreter_service.interpreter import CommandInterpreter
from telegram_integration.telegram_bot import TelegramBot

# Controlador principal do Bud AutoCore

def start_main_controller():
    print("Bud AutoCore iniciado.")
    
    # Inicializa o interpretador de comandos com o caminho base do projeto
    interpreter = CommandInterpreter(base_path="/home/ubuntu/bud_supreme")

    # Exemplo de como um comando pode ser interpretado e gerar modificações
    # Este comando simula a entrada do usuário via Telegram ou outro canal
    print("\nSimulando comando do usuário: \"fique mais agressiva com tendência de alta\"")
    interpreter.interpret_and_modify("fique mais agressiva com tendência de alta")

    print("\nSimulando outro comando do usuário: \"ajuste o gerenciamento de risco\"")
    interpreter.interpret_and_modify("ajuste o gerenciamento de risco")

    # Exemplo de como os serviços podem ser integrados
    # gpt_bridge = GPTBridge()
    # telegram_bot = TelegramBot()
    # telegram_bot.start()
    # ... lógica para conectar os serviços ...

if __name__ == '__main__':
    start_main_controller()


