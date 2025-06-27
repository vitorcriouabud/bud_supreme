import re
import ast
import json
from typing import Dict, List, Any, Optional
from bud_editor_service.editor import CodeEditor
from bud_interpreter_service.gpt_bridge import GPTBridge
from bud_guardian_service.guardian import CodeGuardian
from utils.logger import Logger

class AdvancedCommandInterpreter:
    """
    Interpretador avançado de comandos em linguagem natural para a IA Sorte.
    Capaz de processar comandos complexos e traduzi-los em ações de modificação de código.
    """
    
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.code_editor = CodeEditor(base_path)
        self.gpt_bridge = GPTBridge()
        self.code_guardian = CodeGuardian(base_path)
        self.logger = Logger("AdvancedCommandInterpreter")
        
        # Padrões de comando reconhecidos
        self.command_patterns = {
            'strategy_modification': [
                r'.*mais agressiv.*',
                r'.*estratégia.*agressiv.*',
                r'.*trading.*agressiv.*',
                r'.*aumentar.*agressividade.*',
                r'.*ser mais agressiv.*'
            ],
            'risk_management': [
                r'.*gerenciamento.*risco.*',
                r'.*risk.*management.*',
                r'.*reduzir.*risco.*',
                r'.*aumentar.*risco.*',
                r'.*ajustar.*risco.*'
            ],
            'performance_optimization': [
                r'.*otimizar.*performance.*',
                r'.*melhorar.*velocidade.*',
                r'.*otimizar.*código.*',
                r'.*performance.*melhor.*'
            ],
            'bug_fix': [
                r'.*corrigir.*bug.*',
                r'.*fix.*bug.*',
                r'.*resolver.*erro.*',
                r'.*corrigir.*erro.*'
            ],
            'feature_addition': [
                r'.*adicionar.*funcionalidade.*',
                r'.*nova.*feature.*',
                r'.*implementar.*função.*',
                r'.*criar.*método.*'
            ]
        }
    
    def classify_command(self, command_text: str) -> str:
        """
        Classifica o comando em uma categoria baseada em padrões regex.
        """
        command_lower = command_text.lower()
        
        for category, patterns in self.command_patterns.items():
            for pattern in patterns:
                if re.search(pattern, command_lower):
                    return category
        
        return 'general'
    
    def extract_parameters(self, command_text: str, category: str) -> Dict[str, Any]:
        """
        Extrai parâmetros específicos do comando baseado na categoria.
        """
        parameters = {}
        command_lower = command_text.lower()
        
        if category == 'strategy_modification':
            # Extrair nível de agressividade
            if 'muito agressiv' in command_lower:
                parameters['aggressiveness_level'] = 'high'
            elif 'pouco agressiv' in command_lower:
                parameters['aggressiveness_level'] = 'low'
            else:
                parameters['aggressiveness_level'] = 'medium'
            
            # Extrair direção do mercado
            if 'alta' in command_lower or 'bull' in command_lower:
                parameters['market_direction'] = 'bullish'
            elif 'baixa' in command_lower or 'bear' in command_lower:
                parameters['market_direction'] = 'bearish'
            else:
                parameters['market_direction'] = 'neutral'
        
        elif category == 'risk_management':
            # Extrair tipo de ajuste de risco
            if 'reduzir' in command_lower or 'diminuir' in command_lower:
                parameters['risk_adjustment'] = 'reduce'
            elif 'aumentar' in command_lower or 'elevar' in command_lower:
                parameters['risk_adjustment'] = 'increase'
            else:
                parameters['risk_adjustment'] = 'adjust'
        
        return parameters
    
    def generate_structured_prompt(self, command_text: str, category: str, parameters: Dict[str, Any]) -> str:
        """
        Gera um prompt estruturado para o LLM baseado na categoria e parâmetros.
        """
        base_prompt = f"""
Você é um assistente especializado em modificação de código Python para sistemas de trading.

Comando do usuário: "{command_text}"
Categoria identificada: {category}
Parâmetros extraídos: {json.dumps(parameters, indent=2)}

Instruções específicas:
"""
        
        if category == 'strategy_modification':
            base_prompt += f"""
- Modifique a estratégia de trading no arquivo 'bud_logic/strategy.py'
- Ajuste o nível de agressividade para: {parameters.get('aggressiveness_level', 'medium')}
- Considere a direção do mercado: {parameters.get('market_direction', 'neutral')}
- Mantenha a estrutura existente do código
- Adicione comentários explicativos sobre as modificações
"""
        
        elif category == 'risk_management':
            base_prompt += f"""
- Modifique o gerenciamento de risco no arquivo 'bud_logic/risk_manager.py'
- Tipo de ajuste: {parameters.get('risk_adjustment', 'adjust')}
- Mantenha a compatibilidade com a estratégia existente
- Adicione validações apropriadas
"""
        
        elif category == 'performance_optimization':
            base_prompt += """
- Analise o código existente para identificar gargalos
- Otimize algoritmos e estruturas de dados
- Mantenha a funcionalidade existente
- Adicione comentários sobre as otimizações
"""
        
        base_prompt += """

Responda APENAS com o código Python modificado, sem explicações adicionais.
O código deve ser funcional e seguir as melhores práticas de Python.
"""
        
        return base_prompt
    
    def validate_generated_code(self, code: str) -> bool:
        """
        Valida se o código gerado é sintaticamente correto.
        """
        try:
            ast.parse(code)
            return True
        except SyntaxError as e:
            self.logger.error(f"Código gerado contém erro de sintaxe: {e}")
            return False
    
    def interpret_and_modify(self, command_text: str) -> Dict[str, Any]:
        """
        Interpreta o comando e executa as modificações necessárias.
        """
        self.logger.info(f"Interpretando comando: {command_text}")
        
        # Classificar o comando
        category = self.classify_command(command_text)
        self.logger.info(f"Categoria identificada: {category}")
        
        # Extrair parâmetros
        parameters = self.extract_parameters(command_text, category)
        self.logger.info(f"Parâmetros extraídos: {parameters}")
        
        # Gerar prompt estruturado
        structured_prompt = self.generate_structured_prompt(command_text, category, parameters)
        
        # Usar GPTBridge para gerar código
        modification_result = self.gpt_bridge.process_command(structured_prompt)
        
        if modification_result.get("action") == "generate_code":
            generated_code = modification_result.get("code")
            target_file = modification_result.get("target_file", self.determine_target_file(category))
            
            if generated_code and self.validate_generated_code(generated_code):
                self.logger.info(f"Código gerado validado. Aplicando modificações em {target_file}")
                
                # Aplicar modificações
                success = self.apply_code_modifications(target_file, generated_code, category)
                
                if success:
                    # Executar validações de segurança
                    validation_result = self.run_validations(target_file)
                    
                    return {
                        "status": "success",
                        "category": category,
                        "parameters": parameters,
                        "target_file": target_file,
                        "validation_result": validation_result,
                        "message": f"Comando executado com sucesso. Arquivo {target_file} modificado."
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"Falha ao aplicar modificações no arquivo {target_file}"
                    }
            else:
                return {
                    "status": "error",
                    "message": "Código gerado é inválido ou contém erros de sintaxe"
                }
        else:
            return {
                "status": "error",
                "message": "Falha na geração de código pelo LLM"
            }
    
    def determine_target_file(self, category: str) -> str:
        """
        Determina o arquivo alvo baseado na categoria do comando.
        """
        file_mapping = {
            'strategy_modification': 'bud_logic/strategy.py',
            'risk_management': 'bud_logic/risk_manager.py',
            'performance_optimization': 'bud_logic/strategy.py',
            'bug_fix': 'bud_logic/strategy.py',
            'feature_addition': 'bud_logic/strategy.py'
        }
        
        return file_mapping.get(category, 'bud_logic/strategy.py')
    
    def apply_code_modifications(self, target_file: str, generated_code: str, category: str) -> bool:
        """
        Aplica as modificações de código de forma segura.
        """
        try:
            # Fazer backup do arquivo original
            original_content = self.code_editor.read_file(target_file)
            if original_content:
                backup_file = f"{target_file}.backup"
                self.code_editor.write_file(backup_file, original_content)
                self.logger.info(f"Backup criado: {backup_file}")
            
            # Aplicar as modificações
            if category in ['strategy_modification', 'risk_management']:
                # Para modificações de estratégia e risco, substituir o conteúdo
                self.code_editor.write_file(target_file, generated_code)
            else:
                # Para outras categorias, adicionar ao final
                self.code_editor.append_to_file(target_file, f"\n\n# Modificação automática\n{generated_code}")
            
            self.logger.info(f"Modificações aplicadas com sucesso em {target_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao aplicar modificações: {e}")
            return False
    
    def run_validations(self, target_file: str) -> Dict[str, Any]:
        """
        Executa validações de código e segurança.
        """
        validation_result = {
            "syntax_valid": False,
            "security_check": False,
            "tests_passed": False,
            "details": []
        }
        
        try:
            # Validação sintática
            if self.code_guardian.validate_code(target_file):
                validation_result["syntax_valid"] = True
                validation_result["details"].append("Validação sintática: PASSOU")
            else:
                validation_result["details"].append("Validação sintática: FALHOU")
            
            # Verificação de segurança
            if self.code_guardian.check_security(target_file):
                validation_result["security_check"] = True
                validation_result["details"].append("Verificação de segurança: PASSOU")
            else:
                validation_result["details"].append("Verificação de segurança: FALHOU")
            
            # Execução de testes
            if self.code_guardian.run_tests():
                validation_result["tests_passed"] = True
                validation_result["details"].append("Testes automatizados: PASSOU")
            else:
                validation_result["details"].append("Testes automatizados: FALHOU")
            
        except Exception as e:
            validation_result["details"].append(f"Erro durante validação: {e}")
        
        return validation_result

