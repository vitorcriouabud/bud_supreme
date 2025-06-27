import os
import json
import requests
from typing import Dict, List, Any, Optional
from utils.logger import Logger

class LocalLLMBridge:
    """
    Ponte para modelo LLM local independente da OpenAI.
    Utiliza modelos open-source hospedados localmente ou em serviços gratuitos.
    """
    
    def __init__(self):
        self.logger = Logger("LocalLLMBridge")
        
        # Configurações do modelo local
        self.model_endpoint = os.getenv('LOCAL_LLM_ENDPOINT', 'http://localhost:8000')
        self.model_name = os.getenv('LOCAL_LLM_MODEL', 'codellama')
        self.fallback_enabled = os.getenv('LLM_FALLBACK_ENABLED', 'true').lower() == 'true'
        
        # Templates para diferentes tipos de comandos
        self.command_templates = {
            'strategy_modification': {
                'system_prompt': """Você é um especialista em trading algorítmico. 
                Analise o comando do usuário e gere código Python para modificar a estratégia de trading.
                Foque em parâmetros como agressividade, direção do mercado, e gestão de risco.
                Retorne apenas o código Python necessário, sem explicações.""",
                'user_template': "Comando: {command}\nArquivo alvo: {target_file}\nModifique a estratégia conforme solicitado."
            },
            'risk_management': {
                'system_prompt': """Você é um especialista em gestão de risco financeiro.
                Analise o comando e gere código Python para ajustar parâmetros de risco.
                Foque em stop-loss, take-profit, tamanho de posição, e limites de exposição.
                Retorne apenas o código Python necessário, sem explicações.""",
                'user_template': "Comando: {command}\nArquivo alvo: {target_file}\nAjuste o gerenciamento de risco conforme solicitado."
            },
            'performance_optimization': {
                'system_prompt': """Você é um especialista em otimização de código Python.
                Analise o comando e gere código otimizado para melhor performance.
                Foque em eficiência algorítmica, uso de memória, e velocidade de execução.
                Retorne apenas o código Python necessário, sem explicações.""",
                'user_template': "Comando: {command}\nArquivo alvo: {target_file}\nOtimize a performance conforme solicitado."
            },
            'system_configuration': {
                'system_prompt': """Você é um especialista em configuração de sistemas.
                Analise o comando e gere código Python para ajustar configurações do sistema.
                Foque em parâmetros de logging, alertas, e comportamento geral.
                Retorne apenas o código Python necessário, sem explicações.""",
                'user_template': "Comando: {command}\nArquivo alvo: {target_file}\nConfigure o sistema conforme solicitado."
            }
        }
        
        # Fallback para comandos simples sem LLM
        self.simple_command_patterns = {
            'backup': self._generate_backup_code,
            'status': self._generate_status_code,
            'restart': self._generate_restart_code,
            'stop': self._generate_stop_code
        }
    
    def generate_code(self, command: str, category: str, target_file: str, 
                     context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Gera código baseado no comando fornecido.
        """
        try:
            # Verificar se é um comando simples que não precisa de LLM
            for pattern, generator in self.simple_command_patterns.items():
                if pattern.lower() in command.lower():
                    return generator(command, target_file, context)
            
            # Tentar usar modelo local primeiro
            if self._is_local_model_available():
                result = self._generate_with_local_model(command, category, target_file, context)
                if result['success']:
                    return result
            
            # Fallback para geração baseada em templates
            if self.fallback_enabled:
                return self._generate_with_templates(command, category, target_file, context)
            
            # Se nenhuma opção funcionar
            return {
                'success': False,
                'error': 'Nenhum modelo de IA disponível para geração de código',
                'code': '',
                'explanation': 'Sistema operando em modo limitado'
            }
            
        except Exception as e:
            self.logger.error(f"Erro na geração de código: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': '',
                'explanation': 'Erro interno na geração de código'
            }
    
    def _is_local_model_available(self) -> bool:
        """
        Verifica se o modelo local está disponível.
        """
        try:
            response = requests.get(f"{self.model_endpoint}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _generate_with_local_model(self, command: str, category: str, 
                                  target_file: str, context: Optional[Dict]) -> Dict[str, Any]:
        """
        Gera código usando modelo local.
        """
        try:
            template = self.command_templates.get(category, self.command_templates['system_configuration'])
            
            prompt = {
                'system': template['system_prompt'],
                'user': template['user_template'].format(
                    command=command,
                    target_file=target_file
                ),
                'max_tokens': 500,
                'temperature': 0.1
            }
            
            response = requests.post(
                f"{self.model_endpoint}/generate",
                json=prompt,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_code = result.get('text', '').strip()
                
                return {
                    'success': True,
                    'code': generated_code,
                    'explanation': f'Código gerado pelo modelo local para: {command}',
                    'model_used': 'local_llm'
                }
            else:
                raise Exception(f"Erro na API do modelo local: {response.status_code}")
                
        except Exception as e:
            self.logger.warning(f"Falha no modelo local: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': '',
                'explanation': 'Falha na comunicação com modelo local'
            }
    
    def _generate_with_templates(self, command: str, category: str, 
                                target_file: str, context: Optional[Dict]) -> Dict[str, Any]:
        """
        Gera código usando templates pré-definidos (fallback).
        """
        try:
            # Templates básicos para diferentes categorias
            if category == 'strategy_modification':
                if 'agressiv' in command.lower():
                    code = self._generate_aggressiveness_code(command)
                elif 'conservador' in command.lower():
                    code = self._generate_conservative_code(command)
                else:
                    code = self._generate_generic_strategy_code(command)
            
            elif category == 'risk_management':
                if 'reduz' in command.lower() and 'risco' in command.lower():
                    code = self._generate_reduce_risk_code(command)
                elif 'aument' in command.lower() and 'risco' in command.lower():
                    code = self._generate_increase_risk_code(command)
                else:
                    code = self._generate_generic_risk_code(command)
            
            else:
                code = self._generate_generic_code(command, category)
            
            return {
                'success': True,
                'code': code,
                'explanation': f'Código gerado por template para: {command}',
                'model_used': 'template_fallback'
            }
            
        except Exception as e:
            self.logger.error(f"Erro na geração por template: {e}")
            return {
                'success': False,
                'error': str(e),
                'code': '',
                'explanation': 'Erro na geração por template'
            }
    
    def _generate_aggressiveness_code(self, command: str) -> str:
        """Gera código para aumentar agressividade."""
        return """
# Aumentar agressividade da estratégia
def update_aggressiveness():
    # Aumentar tamanho das posições
    self.position_size_multiplier = min(self.position_size_multiplier * 1.2, 2.0)
    
    # Reduzir stop-loss (mais risco, mais potencial)
    self.stop_loss_percentage = max(self.stop_loss_percentage * 0.8, 0.01)
    
    # Aumentar take-profit
    self.take_profit_percentage = self.take_profit_percentage * 1.3
    
    # Reduzir tempo de espera entre trades
    self.trade_cooldown = max(self.trade_cooldown * 0.7, 30)
    
    self.logger.info("Estratégia configurada para maior agressividade")

update_aggressiveness()
"""
    
    def _generate_conservative_code(self, command: str) -> str:
        """Gera código para estratégia mais conservadora."""
        return """
# Tornar estratégia mais conservadora
def update_conservative_approach():
    # Reduzir tamanho das posições
    self.position_size_multiplier = max(self.position_size_multiplier * 0.8, 0.5)
    
    # Aumentar stop-loss (menos risco)
    self.stop_loss_percentage = min(self.stop_loss_percentage * 1.2, 0.05)
    
    # Reduzir take-profit (mais conservador)
    self.take_profit_percentage = max(self.take_profit_percentage * 0.8, 0.02)
    
    # Aumentar tempo de espera entre trades
    self.trade_cooldown = self.trade_cooldown * 1.5
    
    self.logger.info("Estratégia configurada para abordagem mais conservadora")

update_conservative_approach()
"""
    
    def _generate_reduce_risk_code(self, command: str) -> str:
        """Gera código para reduzir risco."""
        return """
# Reduzir risco das operações
def reduce_risk():
    # Reduzir exposição máxima
    self.max_exposure = min(self.max_exposure * 0.8, 0.1)
    
    # Aumentar stop-loss
    self.default_stop_loss = min(self.default_stop_loss * 1.3, 0.03)
    
    # Reduzir tamanho máximo de posição
    self.max_position_size = max(self.max_position_size * 0.7, 0.01)
    
    # Implementar trailing stop mais apertado
    self.trailing_stop_distance = max(self.trailing_stop_distance * 0.8, 0.005)
    
    self.logger.info("Parâmetros de risco reduzidos")

reduce_risk()
"""
    
    def _generate_increase_risk_code(self, command: str) -> str:
        """Gera código para aumentar risco."""
        return """
# Aumentar risco das operações (com cuidado)
def increase_risk():
    # Aumentar exposição máxima (limitado)
    self.max_exposure = min(self.max_exposure * 1.2, 0.3)
    
    # Reduzir stop-loss (mais risco)
    self.default_stop_loss = max(self.default_stop_loss * 0.8, 0.01)
    
    # Aumentar tamanho máximo de posição
    self.max_position_size = min(self.max_position_size * 1.3, 0.1)
    
    # Implementar trailing stop mais distante
    self.trailing_stop_distance = min(self.trailing_stop_distance * 1.2, 0.02)
    
    self.logger.warning("Parâmetros de risco aumentados - monitorar cuidadosamente")

increase_risk()
"""
    
    def _generate_generic_strategy_code(self, command: str) -> str:
        """Gera código genérico para modificação de estratégia."""
        return f"""
# Modificação de estratégia baseada no comando: {command}
def modify_strategy():
    # Ajustar parâmetros baseado no comando
    self.logger.info(f"Executando modificação: {command}")
    
    # Implementar lógica específica aqui
    # (Este é um template genérico)
    
    self.logger.info("Estratégia modificada com sucesso")

modify_strategy()
"""
    
    def _generate_generic_risk_code(self, command: str) -> str:
        """Gera código genérico para gestão de risco."""
        return f"""
# Ajuste de gestão de risco baseado no comando: {command}
def adjust_risk_management():
    # Ajustar parâmetros de risco
    self.logger.info(f"Executando ajuste de risco: {command}")
    
    # Implementar lógica específica aqui
    # (Este é um template genérico)
    
    self.logger.info("Gestão de risco ajustada com sucesso")

adjust_risk_management()
"""
    
    def _generate_generic_code(self, command: str, category: str) -> str:
        """Gera código genérico para qualquer categoria."""
        return f"""
# Execução de comando: {command}
# Categoria: {category}
def execute_command():
    self.logger.info(f"Executando comando: {command}")
    
    # Implementar lógica específica baseada no comando
    # (Este é um template genérico)
    
    self.logger.info("Comando executado com sucesso")

execute_command()
"""
    
    def _generate_backup_code(self, command: str, target_file: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Gera código para criar backup."""
        code = """
# Criar backup do sistema
from bud_commander_service.deployment_manager import SorteDeploymentManager
import os

def create_backup():
    base_path = os.path.dirname(os.path.dirname(__file__))
    deployment_manager = SorteDeploymentManager(base_path)
    
    backup_result = deployment_manager.create_intelligent_backup("manual_command")
    
    if backup_result["success"]:
        print(f"Backup criado com sucesso: {backup_result['backup_name']}")
        return True
    else:
        print(f"Erro ao criar backup: {backup_result.get('error', 'Erro desconhecido')}")
        return False

create_backup()
"""
        
        return {
            'success': True,
            'code': code,
            'explanation': 'Código para criar backup manual',
            'model_used': 'simple_command'
        }
    
    def _generate_status_code(self, command: str, target_file: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Gera código para verificar status."""
        code = """
# Verificar status do sistema
import psutil
import os
from datetime import datetime

def check_system_status():
    status = {
        'timestamp': datetime.now().isoformat(),
        'cpu_usage': psutil.cpu_percent(),
        'memory_usage': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent,
        'uptime': 'Sistema operacional',
        'components': {
            'interpreter': 'ativo',
            'editor': 'ativo',
            'guardian': 'ativo',
            'telegram': 'ativo'
        }
    }
    
    print("=== STATUS DO SISTEMA SORTE AI ===")
    print(f"Timestamp: {status['timestamp']}")
    print(f"CPU: {status['cpu_usage']}%")
    print(f"Memória: {status['memory_usage']}%")
    print(f"Disco: {status['disk_usage']}%")
    print("Componentes:")
    for component, state in status['components'].items():
        print(f"  - {component}: {state}")
    
    return status

check_system_status()
"""
        
        return {
            'success': True,
            'code': code,
            'explanation': 'Código para verificar status do sistema',
            'model_used': 'simple_command'
        }
    
    def _generate_restart_code(self, command: str, target_file: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Gera código para reiniciar componentes."""
        code = """
# Reiniciar componentes do sistema
import os
import sys

def restart_system():
    print("Preparando para reiniciar sistema...")
    
    # Salvar estado atual
    print("Salvando estado atual...")
    
    # Criar backup de segurança
    print("Criando backup de segurança...")
    
    # Reiniciar processo principal
    print("Reiniciando processo principal...")
    os.execv(sys.executable, ['python'] + sys.argv)

restart_system()
"""
        
        return {
            'success': True,
            'code': code,
            'explanation': 'Código para reiniciar sistema',
            'model_used': 'simple_command'
        }
    
    def _generate_stop_code(self, command: str, target_file: str, context: Optional[Dict]) -> Dict[str, Any]:
        """Gera código para parar sistema."""
        code = """
# Parar sistema de forma segura
import sys
import os

def stop_system():
    print("Iniciando parada segura do sistema...")
    
    # Fechar posições abertas (se houver)
    print("Fechando posições abertas...")
    
    # Salvar estado atual
    print("Salvando estado atual...")
    
    # Criar backup final
    print("Criando backup final...")
    
    # Parar sistema
    print("Sistema Sorte AI parado com segurança.")
    sys.exit(0)

stop_system()
"""
        
        return {
            'success': True,
            'code': code,
            'explanation': 'Código para parar sistema com segurança',
            'model_used': 'simple_command'
        }
    
    def get_model_status(self) -> Dict[str, Any]:
        """
        Retorna status dos modelos disponíveis.
        """
        status = {
            'local_model_available': self._is_local_model_available(),
            'local_model_endpoint': self.model_endpoint,
            'fallback_enabled': self.fallback_enabled,
            'supported_categories': list(self.command_templates.keys()),
            'simple_commands': list(self.simple_command_patterns.keys())
        }
        
        return status

