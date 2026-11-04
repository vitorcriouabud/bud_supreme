import logging
import os
from datetime import datetime
from typing import Optional

class Logger:
    """
    Sistema de logging avançado para a IA Sorte.
    Suporta diferentes níveis de log e formatação estruturada.
    """
    
    def __init__(self, name: str, log_level: str = "INFO", log_file: Optional[str] = None):
        self.name = name
        self.logger = logging.getLogger(name)
        
        # Configurar nível de log
        level_mapping = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        self.logger.setLevel(level_mapping.get(log_level.upper(), logging.INFO))
        
        # Mesmo nome pode ser reutilizado; o arquivo de log precisa ser o solicitado.
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        if not any(
            isinstance(handler, logging.StreamHandler)
            and not isinstance(handler, logging.FileHandler)
            for handler in self.logger.handlers
        ):
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        if log_file:
            target = os.path.abspath(log_file)
            log_dir = os.path.dirname(target)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)

            # Remover arquivos antigos do mesmo logger para evitar gravar em
            # caminhos de testes anteriores (possivelmente já excluídos).
            for handler in list(self.logger.handlers):
                if isinstance(handler, logging.FileHandler) and os.path.abspath(handler.baseFilename) != target:
                    self.logger.removeHandler(handler)
                    handler.close()

            if not any(
                isinstance(handler, logging.FileHandler)
                and os.path.abspath(handler.baseFilename) == target
                for handler in self.logger.handlers
            ):
                file_handler = logging.FileHandler(target, encoding='utf-8')
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        """Log de debug."""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Log de informação."""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Log de aviso."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log de erro."""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Log crítico."""
        self.logger.critical(message)
    
    def log_command_execution(self, command: str, result: dict):
        """Log específico para execução de comandos."""
        status = result.get('status', 'unknown')
        message = f"COMANDO_EXECUTADO: '{command}' | STATUS: {status}"
        
        if status == 'success':
            self.info(message)
        else:
            self.error(message)
    
    def log_code_modification(self, file_path: str, operation: str, success: bool):
        """Log específico para modificações de código."""
        status = "SUCESSO" if success else "FALHA"
        message = f"MODIFICACAO_CODIGO: {file_path} | OPERACAO: {operation} | STATUS: {status}"
        
        if success:
            self.info(message)
        else:
            self.error(message)
    
    def log_validation_result(self, file_path: str, validation_type: str, result: bool):
        """Log específico para resultados de validação."""
        status = "PASSOU" if result else "FALHOU"
        message = f"VALIDACAO: {file_path} | TIPO: {validation_type} | RESULTADO: {status}"
        
        if result:
            self.info(message)
        else:
            self.warning(message)

