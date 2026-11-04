"""Bud Supreme: backup e testes REAIS; código gerado fica em proposta."""
from datetime import datetime, timezone
import json
from pathlib import Path
import uuid

from bud_editor_service.editor import CodeEditor
from bud_guardian_service.guardian import CodeGuardian
from bud_interpreter_service.local_llm import LocalLLMBridge
from core.backup_manager import BackupManager
from utils.logger import Logger


class CommandInterpreter:
    REVIEW_TARGETS = {
        "strategy_modification": "bud_logic/strategy.py",
        "risk_management": "bud_logic/risk_manager.py",
    }

    def __init__(self, base_path=None, llm_bridge=None):
        self.base_path = Path(base_path or Path(__file__).resolve().parent.parent).resolve()
        self.editor = CodeEditor(str(self.base_path))
        self.guardian = CodeGuardian(self.base_path)
        self.backups = BackupManager(self.base_path)
        self.llm_bridge = llm_bridge if llm_bridge is not None else LocalLLMBridge()
        self.logger = Logger("CommandInterpreter")
        self.command_categories = {
            "agressiv": "strategy_modification", "conservador": "strategy_modification",
            "estratégia": "strategy_modification", "estrategia": "strategy_modification",
            "risco": "risk_management", "stop": "risk_management", "profit": "risk_management",
            "otimiz": "performance_optimization", "performance": "performance_optimization",
            "velocidade": "performance_optimization", "config": "system_configuration",
            "alert": "system_configuration", "log": "system_configuration",
        }
        self.target_files = dict(self.REVIEW_TARGETS)

    def _classify_command(self, command):
        lower = command.lower()
        for keyword, category in self.command_categories.items():
            if keyword in lower:
                return category
        return "system_configuration"

    def interpret_command(self, command):
        category = self._classify_command(command)
        if category not in self.REVIEW_TARGETS:
            return {"success": False, "command": command,
                    "error": "Comando ainda não habilitado. Use backup, status ou executar testes."}
        target = self.REVIEW_TARGETS[category]
        try:
            output = self.llm_bridge.generate_code(
                command=command, category=category, target_file=target,
            )
            if not output.get("success"):
                return {"success": False, "command": command,
                        "error": output.get("error", "Falha ao gerar código")}
            code = output.get("code", "")
            if not self.guardian.validate_source(code):
                return {"success": False, "command": command,
                        "error": "Código vazio ou sintaxe inválida"}
            if not self.guardian.check_source_security(code):
                return {"success": False, "command": command,
                        "error": "Proposta rejeitada pelo filtro estático"}
            return {
                "success": True, "command": command, "category": category,
                "target_file": target, "generated_code": code,
                "model_used": output.get("model_used", "unknown"),
                "validation_passed": True, "applied": False,
            }
        except Exception as exc:
            return {"success": False, "command": command, "error": str(exc)}

    def execute_command(self, command):
        if not isinstance(command, str) or not command.strip():
            return {"success": False, "error": "Comando vazio"}
        lower = command.strip().lower()
        if lower in {"status", "status do sistema", "ver status", "/status"}:
            return {"success": True, "command": command, "action": "status",
                    "status": self.get_status(), "applied": False, "tests_passed": None,
                    "explanation": "Estado consultado; nenhum teste foi executado"}
        if "backup" in lower:
            backup = self.backups.create_backup(reason="command")
            return {**backup, "command": command, "action": "backup", "applied": False,
                    "tests_passed": None, "model_used": "built_in",
                    "explanation": "Backup real verificado" if backup["success"] else backup.get("error")}
        if lower in {"testes", "executar testes", "rodar testes", "testar sistema"}:
            passed = self.guardian.run_tests()
            return {"success": passed, "command": command, "action": "tests",
                    "applied": False, "tests_passed": passed,
                    "test_results": self.guardian.last_test_result,
                    "model_used": "built_in",
                    "explanation": "Testes realmente executados" if passed else "Falha nos testes"}
        result = self.interpret_command(command)
        if not result.get("success"):
            return result
        try:
            folder = self.base_path / "proposals"
            folder.mkdir(parents=True, exist_ok=True)
            identifier = uuid.uuid4().hex
            code_file = folder / (identifier + ".py")
            info_file = folder / (identifier + ".json")
            details = {
                "id": identifier, "timestamp": datetime.now(timezone.utc).isoformat(),
                "command": command, "target_file": result["target_file"],
                "model_used": result["model_used"], "applied": False,
                "tests_passed": None, "notice": "Somente proposta. Trading real desabilitado.",
            }
            with code_file.open("x", encoding="utf-8") as handle:
                handle.write(result["generated_code"])
            with info_file.open("x", encoding="utf-8") as handle:
                json.dump(details, handle, ensure_ascii=False, indent=2)
            return {
                "success": True, "command": command, "category": result["category"],
                "target_file": result["target_file"],
                "proposal_created": code_file.relative_to(self.base_path).as_posix(),
                "model_used": result["model_used"], "applied": False, "tests_passed": None,
                "explanation": "Proposta salva para revisão; código original não alterado.",
            }
        except Exception as exc:
            return {"success": False, "command": command, "error": str(exc)}

    def get_status(self):
        try:
            llm = self.llm_bridge.get_model_status()
        except Exception as exc:
            llm = {"available": False, "error": str(exc)}
        return {
            "interpreter_status": "active",
            "llm_bridge_status": llm,
            "editor_status": "review_only",
            "guardian_status": "available_not_run",
            "code_apply_mode": "review_only",
            "trading_real": "disabled",
            "supported_categories": list(self.REVIEW_TARGETS),
            "target_files": self.target_files,
            "base_path": str(self.base_path),
        }
