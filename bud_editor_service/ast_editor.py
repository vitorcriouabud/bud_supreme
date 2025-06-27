import ast
import os
import shutil
from typing import Dict, List, Any, Optional, Union
from utils.logger import Logger

class ASTCodeEditor:
    """
    Editor de código avançado que manipula a Abstract Syntax Tree (AST) do Python
    para modificações mais seguras e semanticamente corretas.
    """
    
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.logger = Logger("ASTCodeEditor")
    
    def read_file(self, relative_path: str) -> Optional[str]:
        """Lê o conteúdo de um arquivo."""
        file_path = os.path.join(self.base_path, relative_path)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            self.logger.error(f"Arquivo não encontrado: {file_path}")
            return None
        except Exception as e:
            self.logger.error(f"Erro ao ler arquivo {file_path}: {e}")
            return None
    
    def write_file(self, relative_path: str, content: str) -> bool:
        """Escreve conteúdo em um arquivo."""
        file_path = os.path.join(self.base_path, relative_path)
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.logger.log_code_modification(relative_path, "WRITE", True)
            return True
        except Exception as e:
            self.logger.error(f"Erro ao escrever arquivo {file_path}: {e}")
            self.logger.log_code_modification(relative_path, "WRITE", False)
            return False
    
    def create_backup(self, relative_path: str) -> bool:
        """Cria um backup do arquivo antes de modificá-lo."""
        file_path = os.path.join(self.base_path, relative_path)
        backup_path = f"{file_path}.backup"
        
        try:
            if os.path.exists(file_path):
                shutil.copy2(file_path, backup_path)
                self.logger.info(f"Backup criado: {backup_path}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Erro ao criar backup: {e}")
            return False
    
    def restore_backup(self, relative_path: str) -> bool:
        """Restaura um arquivo a partir do backup."""
        file_path = os.path.join(self.base_path, relative_path)
        backup_path = f"{file_path}.backup"
        
        try:
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, file_path)
                self.logger.info(f"Arquivo restaurado do backup: {file_path}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Erro ao restaurar backup: {e}")
            return False
    
    def parse_code(self, code: str) -> Optional[ast.AST]:
        """Analisa o código Python e retorna a AST."""
        try:
            return ast.parse(code)
        except SyntaxError as e:
            self.logger.error(f"Erro de sintaxe no código: {e}")
            return None
    
    def ast_to_code(self, tree: ast.AST) -> str:
        """Converte uma AST de volta para código Python."""
        try:
            import astor
            return astor.to_source(tree)
        except ImportError:
            # Fallback para ast.unparse (Python 3.9+)
            try:
                return ast.unparse(tree)
            except AttributeError:
                self.logger.error("Biblioteca 'astor' não encontrada e ast.unparse não disponível")
                return ""
    
    def find_function_node(self, tree: ast.AST, function_name: str) -> Optional[ast.FunctionDef]:
        """Encontra um nó de função específico na AST."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                return node
        return None
    
    def find_class_node(self, tree: ast.AST, class_name: str) -> Optional[ast.ClassDef]:
        """Encontra um nó de classe específico na AST."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                return node
        return None
    
    def add_function_to_class(self, relative_path: str, class_name: str, function_code: str) -> bool:
        """Adiciona uma função a uma classe existente."""
        content = self.read_file(relative_path)
        if not content:
            return False
        
        # Criar backup
        self.create_backup(relative_path)
        
        try:
            tree = self.parse_code(content)
            if not tree:
                return False
            
            # Encontrar a classe
            class_node = self.find_class_node(tree, class_name)
            if not class_node:
                self.logger.error(f"Classe '{class_name}' não encontrada")
                return False
            
            # Analisar o código da nova função
            function_tree = self.parse_code(function_code)
            if not function_tree:
                return False
            
            # Adicionar a função à classe
            for node in function_tree.body:
                if isinstance(node, ast.FunctionDef):
                    class_node.body.append(node)
            
            # Converter de volta para código
            new_code = self.ast_to_code(tree)
            
            # Escrever o arquivo modificado
            success = self.write_file(relative_path, new_code)
            self.logger.log_code_modification(relative_path, f"ADD_FUNCTION_TO_CLASS:{class_name}", success)
            return success
            
        except Exception as e:
            self.logger.error(f"Erro ao adicionar função à classe: {e}")
            self.restore_backup(relative_path)
            return False
    
    def modify_function_body(self, relative_path: str, function_name: str, new_body_code: str) -> bool:
        """Modifica o corpo de uma função existente."""
        content = self.read_file(relative_path)
        if not content:
            return False
        
        # Criar backup
        self.create_backup(relative_path)
        
        try:
            tree = self.parse_code(content)
            if not tree:
                return False
            
            # Encontrar a função
            function_node = self.find_function_node(tree, function_name)
            if not function_node:
                self.logger.error(f"Função '{function_name}' não encontrada")
                return False
            
            # Analisar o novo corpo da função
            new_body_tree = self.parse_code(new_body_code)
            if not new_body_tree:
                return False
            
            # Substituir o corpo da função
            function_node.body = new_body_tree.body
            
            # Converter de volta para código
            new_code = self.ast_to_code(tree)
            
            # Escrever o arquivo modificado
            success = self.write_file(relative_path, new_code)
            self.logger.log_code_modification(relative_path, f"MODIFY_FUNCTION:{function_name}", success)
            return success
            
        except Exception as e:
            self.logger.error(f"Erro ao modificar função: {e}")
            self.restore_backup(relative_path)
            return False
    
    def add_import(self, relative_path: str, import_statement: str) -> bool:
        """Adiciona uma declaração de import ao arquivo."""
        content = self.read_file(relative_path)
        if not content:
            return False
        
        # Verificar se o import já existe
        if import_statement in content:
            self.logger.info(f"Import já existe: {import_statement}")
            return True
        
        # Criar backup
        self.create_backup(relative_path)
        
        try:
            tree = self.parse_code(content)
            if not tree:
                return False
            
            # Analisar a declaração de import
            import_tree = self.parse_code(import_statement)
            if not import_tree:
                return False
            
            # Adicionar o import no início do arquivo
            for node in import_tree.body:
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    tree.body.insert(0, node)
            
            # Converter de volta para código
            new_code = self.ast_to_code(tree)
            
            # Escrever o arquivo modificado
            success = self.write_file(relative_path, new_code)
            self.logger.log_code_modification(relative_path, f"ADD_IMPORT", success)
            return success
            
        except Exception as e:
            self.logger.error(f"Erro ao adicionar import: {e}")
            self.restore_backup(relative_path)
            return False
    
    def validate_syntax(self, code: str) -> bool:
        """Valida se o código Python tem sintaxe correta."""
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False
    
    def get_function_names(self, relative_path: str) -> List[str]:
        """Retorna uma lista com os nomes de todas as funções no arquivo."""
        content = self.read_file(relative_path)
        if not content:
            return []
        
        tree = self.parse_code(content)
        if not tree:
            return []
        
        function_names = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                function_names.append(node.name)
        
        return function_names
    
    def get_class_names(self, relative_path: str) -> List[str]:
        """Retorna uma lista com os nomes de todas as classes no arquivo."""
        content = self.read_file(relative_path)
        if not content:
            return []
        
        tree = self.parse_code(content)
        if not tree:
            return []
        
        class_names = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_names.append(node.name)
        
        return class_names

