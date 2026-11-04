"""Validação de sintaxe e testes reais. Filtro estático NÃO é sandbox."""
import ast
from pathlib import Path
import subprocess
import sys
from utils.logger import Logger


class CodeGuardian:
    BLOCKED_IMPORTS = {
        "MetaTrader5", "subprocess", "socket", "ctypes", "paramiko",
        "requests", "urllib", "http", "ftplib",
    }
    BLOCKED_CALLS = {
        "eval", "exec", "compile", "__import__", "open", "breakpoint",
        "system", "popen", "Popen", "run", "call", "check_call",
        "check_output", "order_send", "order_check", "withdraw", "transfer",
    }

    def __init__(self, base_path):
        self.root = Path(base_path).resolve()
        self.logger = Logger("CodeGuardian")
        self.last_test_result = None

    def _safe_path(self, file_path):
        p = (self.root / file_path).resolve()
        if p == self.root or not p.is_relative_to(self.root):
            raise ValueError("Caminho fora do repositório")
        return p

    def validate_source(self, source):
        try:
            if not isinstance(source, str) or not source.strip():
                return False
            ast.parse(source)
            return True
        except (SyntaxError, TypeError, ValueError):
            return False

    def check_source_security(self, source):
        if not self.validate_source(source):
            return False
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Import):
                if any(item.name.split(".")[0] in self.BLOCKED_IMPORTS for item in node.names):
                    return False
            elif isinstance(node, ast.ImportFrom):
                if (node.module or "").split(".")[0] in self.BLOCKED_IMPORTS:
                    return False
            elif isinstance(node, ast.Call):
                f = node.func
                name = f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else None
                if name in self.BLOCKED_CALLS:
                    return False
        return True

    def validate_code(self, file_path):
        try:
            return self.validate_source(self._safe_path(file_path).read_text(encoding="utf-8"))
        except (OSError, ValueError, UnicodeError):
            return False

    def check_security(self, file_path):
        try:
            return self.check_source_security(self._safe_path(file_path).read_text(encoding="utf-8"))
        except (OSError, ValueError, UnicodeError):
            return False

    def run_pylint_analysis(self, file_path):
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pylint", str(self._safe_path(file_path))],
                cwd=self.root, capture_output=True, text=True, timeout=60,
            )
            return result.returncode == 0
        except (OSError, ValueError, subprocess.TimeoutExpired):
            return False

    def run_tests(self):
        if not (self.root / "tests").is_dir():
            self.last_test_result = {"passed": False, "error": "Pasta tests ausente"}
            return False
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "-q", "tests"],
                cwd=self.root, capture_output=True, text=True, timeout=180,
            )
            passed = result.returncode == 0
            self.last_test_result = {
                "passed": passed, "exit_code": result.returncode,
                "stdout": result.stdout[-5000:], "stderr": result.stderr[-3000:],
            }
            return passed
        except (OSError, subprocess.TimeoutExpired) as exc:
            self.last_test_result = {"passed": False, "error": str(exc)}
            return False
