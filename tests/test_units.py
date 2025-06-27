import unittest
import tempfile
import os
import shutil
from unittest.mock import Mock, patch, MagicMock
import sys

# Adicionar o diretório base ao path para importações
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestAdvancedCommandInterpreter(unittest.TestCase):
    """Testes unitários para o AdvancedCommandInterpreter."""
    
    def setUp(self):
        """Configuração inicial para cada teste."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock das dependências
        with patch('bud_interpreter_service.advanced_interpreter.CodeEditor'), \
             patch('bud_interpreter_service.advanced_interpreter.GPTBridge'), \
             patch('bud_interpreter_service.advanced_interpreter.CodeGuardian'), \
             patch('bud_interpreter_service.advanced_interpreter.Logger'):
            
            from bud_interpreter_service.advanced_interpreter import AdvancedCommandInterpreter
            self.interpreter = AdvancedCommandInterpreter(self.temp_dir)
    
    def tearDown(self):
        """Limpeza após cada teste."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_classify_command_strategy_modification(self):
        """Testa classificação de comandos de modificação de estratégia."""
        commands = [
            "seja mais agressiva com tendência de alta",
            "fique mais agressiva",
            "estratégia mais agressiva",
            "aumentar agressividade"
        ]
        
        for cmd in commands:
            result = self.interpreter.classify_command(cmd)
            self.assertEqual(result, 'strategy_modification', 
                           f"Comando '{cmd}' deveria ser classificado como 'strategy_modification'")
    
    def test_classify_command_risk_management(self):
        """Testa classificação de comandos de gerenciamento de risco."""
        commands = [
            "ajuste o gerenciamento de risco",
            "reduzir risco das operações",
            "aumentar o risco",
            "gerenciamento de risco"
        ]
        
        for cmd in commands:
            result = self.interpreter.classify_command(cmd)
            self.assertEqual(result, 'risk_management',
                           f"Comando '{cmd}' deveria ser classificado como 'risk_management'")
    
    def test_extract_parameters_strategy(self):
        """Testa extração de parâmetros para comandos de estratégia."""
        # Teste de nível de agressividade
        result = self.interpreter.extract_parameters("seja muito agressiva", "strategy_modification")
        self.assertEqual(result['aggressiveness_level'], 'high')
        
        result = self.interpreter.extract_parameters("seja pouco agressiva", "strategy_modification")
        self.assertEqual(result['aggressiveness_level'], 'low')
        
        # Teste de direção do mercado
        result = self.interpreter.extract_parameters("tendência de alta", "strategy_modification")
        self.assertEqual(result['market_direction'], 'bullish')
        
        result = self.interpreter.extract_parameters("mercado de baixa", "strategy_modification")
        self.assertEqual(result['market_direction'], 'bearish')
    
    def test_extract_parameters_risk(self):
        """Testa extração de parâmetros para comandos de risco."""
        result = self.interpreter.extract_parameters("reduzir o risco", "risk_management")
        self.assertEqual(result['risk_adjustment'], 'reduce')
        
        result = self.interpreter.extract_parameters("aumentar o risco", "risk_management")
        self.assertEqual(result['risk_adjustment'], 'increase')
    
    def test_determine_target_file(self):
        """Testa determinação do arquivo alvo baseado na categoria."""
        self.assertEqual(
            self.interpreter.determine_target_file('strategy_modification'),
            'bud_logic/strategy.py'
        )
        
        self.assertEqual(
            self.interpreter.determine_target_file('risk_management'),
            'bud_logic/risk_manager.py'
        )
    
    def test_validate_generated_code(self):
        """Testa validação de código gerado."""
        # Código válido
        valid_code = """
def test_function():
    return True
"""
        self.assertTrue(self.interpreter.validate_generated_code(valid_code))
        
        # Código inválido
        invalid_code = """
def test_function(
    return True  # Parênteses não fechados
"""
        self.assertFalse(self.interpreter.validate_generated_code(invalid_code))


class TestASTCodeEditor(unittest.TestCase):
    """Testes unitários para o ASTCodeEditor."""
    
    def setUp(self):
        """Configuração inicial para cada teste."""
        self.temp_dir = tempfile.mkdtemp()
        
        with patch('bud_editor_service.ast_editor.Logger'):
            from bud_editor_service.ast_editor import ASTCodeEditor
            self.editor = ASTCodeEditor(self.temp_dir)
    
    def tearDown(self):
        """Limpeza após cada teste."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_write_and_read_file(self):
        """Testa escrita e leitura de arquivos."""
        test_content = "print('Hello, World!')"
        test_file = "test.py"
        
        # Escrever arquivo
        success = self.editor.write_file(test_file, test_content)
        self.assertTrue(success)
        
        # Ler arquivo
        content = self.editor.read_file(test_file)
        self.assertEqual(content, test_content)
    
    def test_create_and_restore_backup(self):
        """Testa criação e restauração de backup."""
        test_content = "original_content = True"
        test_file = "backup_test.py"
        
        # Criar arquivo original
        self.editor.write_file(test_file, test_content)
        
        # Criar backup
        backup_success = self.editor.create_backup(test_file)
        self.assertTrue(backup_success)
        
        # Modificar arquivo original
        modified_content = "modified_content = True"
        self.editor.write_file(test_file, modified_content)
        
        # Verificar que foi modificado
        current_content = self.editor.read_file(test_file)
        self.assertEqual(current_content, modified_content)
        
        # Restaurar backup
        restore_success = self.editor.restore_backup(test_file)
        self.assertTrue(restore_success)
        
        # Verificar que foi restaurado
        restored_content = self.editor.read_file(test_file)
        self.assertEqual(restored_content, test_content)
    
    def test_parse_code(self):
        """Testa análise de código Python."""
        valid_code = """
def hello():
    print("Hello, World!")
    return True
"""
        
        tree = self.editor.parse_code(valid_code)
        self.assertIsNotNone(tree)
        
        # Código inválido
        invalid_code = "def hello(\n    print('invalid')"
        tree = self.editor.parse_code(invalid_code)
        self.assertIsNone(tree)
    
    def test_validate_syntax(self):
        """Testa validação de sintaxe."""
        valid_code = "def test(): return True"
        self.assertTrue(self.editor.validate_syntax(valid_code))
        
        invalid_code = "def test( return True"
        self.assertFalse(self.editor.validate_syntax(invalid_code))
    
    def test_get_function_names(self):
        """Testa extração de nomes de funções."""
        code_with_functions = """
def function_one():
    pass

def function_two():
    return True

class TestClass:
    def method_one(self):
        pass
"""
        
        test_file = "functions_test.py"
        self.editor.write_file(test_file, code_with_functions)
        
        function_names = self.editor.get_function_names(test_file)
        expected_names = ['function_one', 'function_two', 'method_one']
        
        for name in expected_names:
            self.assertIn(name, function_names)
    
    def test_get_class_names(self):
        """Testa extração de nomes de classes."""
        code_with_classes = """
class ClassOne:
    pass

class ClassTwo:
    def method(self):
        pass

def standalone_function():
    pass
"""
        
        test_file = "classes_test.py"
        self.editor.write_file(test_file, code_with_classes)
        
        class_names = self.editor.get_class_names(test_file)
        expected_names = ['ClassOne', 'ClassTwo']
        
        for name in expected_names:
            self.assertIn(name, class_names)


class TestCodeGuardian(unittest.TestCase):
    """Testes unitários para o CodeGuardian."""
    
    def setUp(self):
        """Configuração inicial para cada teste."""
        self.temp_dir = tempfile.mkdtemp()
        
        with patch('bud_guardian_service.guardian.Logger'):
            from bud_guardian_service.guardian import CodeGuardian
            self.guardian = CodeGuardian(self.temp_dir)
    
    def tearDown(self):
        """Limpeza após cada teste."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_validate_code_valid(self):
        """Testa validação de código válido."""
        valid_code = """
def calculate_profit(price, quantity):
    return price * quantity

class TradingStrategy:
    def __init__(self):
        self.name = "Test Strategy"
    
    def execute(self):
        return True
"""
        
        test_file = "valid_code.py"
        with open(os.path.join(self.temp_dir, test_file), 'w') as f:
            f.write(valid_code)
        
        result = self.guardian.validate_code(test_file)
        self.assertTrue(result)
    
    def test_validate_code_invalid(self):
        """Testa validação de código inválido."""
        invalid_code = """
def calculate_profit(price, quantity
    return price * quantity  # Parênteses não fechados
"""
        
        test_file = "invalid_code.py"
        with open(os.path.join(self.temp_dir, test_file), 'w') as f:
            f.write(invalid_code)
        
        result = self.guardian.validate_code(test_file)
        self.assertFalse(result)
    
    @patch('subprocess.run')
    def test_run_pylint_analysis(self, mock_subprocess):
        """Testa execução da análise Pylint."""
        # Mock da resposta do subprocess
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Your code has been rated at 10.00/10"
        mock_subprocess.return_value = mock_result
        
        test_file = "pylint_test.py"
        with open(os.path.join(self.temp_dir, test_file), 'w') as f:
            f.write("def test(): return True")
        
        result = self.guardian.run_pylint_analysis(test_file)
        self.assertTrue(result)
        
        # Verificar se o subprocess foi chamado corretamente
        mock_subprocess.assert_called_once()


class TestSorteLogger(unittest.TestCase):
    """Testes unitários para o Logger da Sorte."""
    
    def setUp(self):
        """Configuração inicial para cada teste."""
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "test.log")
    
    def tearDown(self):
        """Limpeza após cada teste."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_logger_initialization(self):
        """Testa inicialização do logger."""
        from utils.logger import Logger
        
        logger = Logger("TestLogger", "INFO", self.log_file)
        self.assertEqual(logger.name, "TestLogger")
        self.assertIsNotNone(logger.logger)
    
    def test_log_levels(self):
        """Testa diferentes níveis de log."""
        from utils.logger import Logger
        
        logger = Logger("TestLogger", "DEBUG", self.log_file)
        
        # Testar se os métodos existem e podem ser chamados
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")
        
        # Verificar se o arquivo de log foi criado
        self.assertTrue(os.path.exists(self.log_file))
    
    def test_log_command_execution(self):
        """Testa log específico para execução de comandos."""
        from utils.logger import Logger
        
        logger = Logger("TestLogger", "INFO", self.log_file)
        
        # Comando bem-sucedido
        result_success = {"status": "success", "message": "Command executed"}
        logger.log_command_execution("test command", result_success)
        
        # Comando com falha
        result_error = {"status": "error", "message": "Command failed"}
        logger.log_command_execution("test command", result_error)
        
        # Verificar se o arquivo de log foi criado
        self.assertTrue(os.path.exists(self.log_file))
    
    def test_log_code_modification(self):
        """Testa log específico para modificações de código."""
        from utils.logger import Logger
        
        logger = Logger("TestLogger", "INFO", self.log_file)
        
        # Modificação bem-sucedida
        logger.log_code_modification("test.py", "ADD_FUNCTION", True)
        
        # Modificação com falha
        logger.log_code_modification("test.py", "MODIFY_FUNCTION", False)
        
        # Verificar se o arquivo de log foi criado
        self.assertTrue(os.path.exists(self.log_file))


if __name__ == '__main__':
    # Executar todos os testes
    unittest.main(verbosity=2)

