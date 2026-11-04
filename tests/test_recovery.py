"""Regressão: backups e testes não podem ser simulados."""
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import zipfile

from core.backup_manager import BackupManager
from bud_guardian_service.guardian import CodeGuardian
from bud_interpreter_service.interpreter import CommandInterpreter


class FakeLLM:
    def __init__(self, code="def strategy():\n    return 1\n"):
        self.code = code

    def generate_code(self, command, category, target_file):
        return {"success": True, "code": self.code, "model_used": "fake"}

    def get_model_status(self):
        return {"local_model_available": False, "fallback_enabled": False}


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "bud_logic").mkdir()
        (self.root / "bud_logic" / "strategy.py").write_text("ORIGINAL = 1\n", encoding="utf-8")
        (self.root / "tests").mkdir()
        (self.root / "tests" / "test_dummy.py").write_text("def test_ok(): assert True\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_backup_exists_with_source(self):
        result = BackupManager(self.root).create_backup()
        self.assertTrue(result["success"], result)
        with zipfile.ZipFile(self.root / result["backup_created"]) as archive:
            self.assertEqual(archive.read("bud_logic/strategy.py"), b"ORIGINAL = 1\n")

    def test_backup_never_includes_env_or_database(self):
        (self.root / ".env").write_text("SECRET", encoding="utf-8")
        (self.root / "bud_logic" / ".env.local").write_text("SECRET", encoding="utf-8")
        (self.root / "bud_logic" / "data.db").write_bytes(b"SECRET")
        result = BackupManager(self.root).create_backup()
        with zipfile.ZipFile(self.root / result["backup_created"]) as archive:
            self.assertNotIn(".env", archive.namelist())
            self.assertNotIn("bud_logic/.env.local", archive.namelist())
            self.assertNotIn("bud_logic/data.db", archive.namelist())

    def test_empty_backup_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertFalse(BackupManager(tmp).create_backup()["success"])

    def test_backup_without_ai(self):
        interpreter = CommandInterpreter(self.root, FakeLLM())
        output = interpreter.execute_command("criar backup manual")
        self.assertTrue(output["success"])
        self.assertTrue((self.root / output["backup_created"]).exists())
        self.assertIsNone(output["tests_passed"])

    def test_ai_proposes_but_does_not_overwrite(self):
        interpreter = CommandInterpreter(self.root, FakeLLM())
        output = interpreter.execute_command("aumentar risco")
        self.assertTrue(output["success"], output)
        self.assertFalse(output["applied"])
        self.assertIsNone(output["tests_passed"])
        self.assertTrue((self.root / output["proposal_created"]).exists())
        self.assertEqual((self.root / "bud_logic/strategy.py").read_text(encoding="utf-8"), "ORIGINAL = 1\n")

    def test_unsafe_code_or_invalid_syntax_fails(self):
        for code in ("def broken(:\n", "import MetaTrader5\n", "exec('print(1)')\n"):
            with self.subTest(code=code):
                interpreter = CommandInterpreter(self.root, FakeLLM(code))
                self.assertFalse(interpreter.execute_command("aumentar risco")["success"])

    def test_unsupported_instruction_fails(self):
        interpreter = CommandInterpreter(self.root, FakeLLM())
        self.assertFalse(interpreter.execute_command("configurar sistema")["success"])

    def test_real_exit_codes(self):
        guardian = CodeGuardian(self.root)
        for code in (0, 1, 5):
            class Result:
                returncode = code
                stdout = "pytest result"
                stderr = ""
            with patch("bud_guardian_service.guardian.subprocess.run", return_value=Result()) as mock:
                self.assertEqual(guardian.run_tests(), code == 0)
                self.assertEqual(guardian.last_test_result["exit_code"], code)
                mock.assert_called_once()

    def test_missing_tests_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertFalse(CodeGuardian(tmp).run_tests())

    def test_guardian_blocks_outside_path(self):
        guardian = CodeGuardian(self.root)
        self.assertFalse(guardian.validate_code("../outside.py"))
        self.assertFalse(guardian.check_source_security("import subprocess\n"))
        self.assertFalse(guardian.check_source_security("eval('1+1')\n"))
        self.assertTrue(guardian.check_source_security("def f():\n    return 2\n"))
