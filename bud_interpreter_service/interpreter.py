from bud_editor_service.editor import CodeEditor
from bud_guardian_service.guardian import CodeGuardian
from bud_interpreter_service.local_llm import LocalLLMBridge
from utils.logger import Logger
import re
import os

class CommandInterpreter:
    def __init__(self):
        self.editor = CodeEditor()
        self.guardian = CodeGuardian()
        self.llm_bridge = LocalLLMBridge()
        self.logger = Logger("CommandInterpreter")
        
        # Mapeamento de comandos para categorias
        self.command_categories = {
            'agressiv': 'strategy_modification',
            'conservador': 'strategy_modification',
            'estratégia': 'strategy_modification',
            'risco': 'risk_management',
            'stop': 'risk_management',
            'profit': 'risk_management',
            'otimiz': 'performance_optimization',
            'performance': 'performance_optimization',
            'velocidade': 'performance_optimization',
            'config': 'system_configuration',
            'alert': 'system_configuration',
            'log': 'system_configuration'
        }
        
        # Mapeamento de comandos para arquivos alvo
        self.target_files = {
            'strategy_modification': 'bud_logic/strategy.py',
            'risk_management': 'bud_logic/risk_manager.py',
            'performance_optimization': 'core/main_controller.py',
            'system_configuration': 'config.yaml'
        }
    
    def interpret_command(self, command: str) -> dict:
        """
        Interpreta um comando em linguagem natural e retorna instruções para execução.
        """
        try:
            self.logger.info(f"Interpretando comando: {command}")
            
            # Classificar categoria do comando
            category = self._classify_command(command)
            
            # Determinar arquivo alvo
            target_file = self.target_files.get(category, 'core/main_controller.py')
            
            # Gerar código usando LLM local
            generation_result = self.llm_bridge.generate_code(
                command=command,
                category=category,
                target_file=target_file
            )
            
            if not generation_result['success']:
                return {
                    'success': False,
                    'error': generation_result['error'],
                    'command': command
                }
            
            # Validar código gerado
            validation_result = self.guardian.validate_code(generation_result['code'])
            
            if not validation_result['is_safe']:
                return {
                    'success': False,
                    'error': f"Código gerado não passou na validação: {validation_result['issues']}",
                    'command': command
                }
            
            return {
                'success': True,
                'command': command,
                'category': category,
                'target_file': target_file,
                'generated_code': generation_result['code'],
                'explanation': generation_result['explanation'],
                'model_used': generation_result.get('model_used', 'unknown'),
                'validation_passed': True
            }
            
        except Exception as e:
            self.logger.error(f"Erro na interpretação do comando: {e}")
            return {
                'success': False,
                'error': str(e),
                'command': command
            }
    
    def execute_command(self, command: str) -> dict:
        """
        Interpreta e executa um comando completo.
        """
        try:
            # Interpretar comando
            interpretation_result = self.interpret_command(command)
            
            if not interpretation_result['success']:
                return interpretation_result
            
            # Executar modificação de código
            execution_result = self.editor.modify_code(
                file_path=interpretation_result['target_file'],
                new_code=interpretation_result['generated_code'],
                backup=True
            )
            
            if not execution_result['success']:
                return {
                    'success': False,
                    'error': f"Erro na execução: {execution_result['error']}",
                    'command': command
                }
            
            # Executar testes pós-modificação
            test_result = self.guardian.run_tests()
            
            result = {
                'success': True,
                'command': command,
                'category': interpretation_result['category'],
                'target_file': interpretation_result['target_file'],
                'explanation': interpretation_result['explanation'],
                'model_used': interpretation_result.get('model_used', 'unknown'),
                'backup_created': execution_result.get('backup_path'),
                'tests_passed': test_result.get('passed', False),
                'test_results': test_result
            }
            
            self.logger.info(f"Comando executado com sucesso: {command}")
            return result
            
        except Exception as e:
            self.logger.error(f"Erro na execução do comando: {e}")
            return {
                'success': False,
                'error': str(e),
                'command': command
            }
    
    def _classify_command(self, command: str) -> str:
        """
        Classifica um comando em uma categoria.
        """
        command_lower = command.lower()
        
        for keyword, category in self.command_categories.items():
            if keyword in command_lower:
                return category
        
        # Categoria padrão
        return 'system_configuration'
    
    def get_status(self) -> dict:
        """
        Retorna status do interpretador e componentes.
        """
        return {
            'interpreter_status': 'active',
            'llm_bridge_status': self.llm_bridge.get_model_status(),
            'editor_status': 'active',
            'guardian_status': 'active',
            'supported_categories': list(self.command_categories.values()),
            'target_files': self.target_files
        }

