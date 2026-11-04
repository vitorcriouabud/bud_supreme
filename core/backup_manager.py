"""Backups reais de código; exclui credenciais, ambientes e bancos de dados."""
from datetime import datetime, timezone
from pathlib import Path
import os
import uuid
import zipfile


class BackupManager:
    DIRECTORIES = (
        "core", "bud_commander_service", "bud_editor_service",
        "bud_guardian_service", "bud_interpreter_service", "bud_logic",
        "telegram_integration", "utils", "tests", "sorte_dashboard/src",
    )
    FILES = (
        "Dockerfile", "Procfile", "requirements.txt", "config.yaml",
        "docker-compose.yml", "railway.json", "nixpacks.toml",
        ".gitignore", "README.md", "QUICK_START.md",
    )
    ALLOWED = {".py", ".txt", ".md", ".toml", ".yml", ".yaml", ".json", ".html", ".css", ".js"}
    SKIP_DIRS = {".git", "venv", ".venv", "__pycache__", ".pytest_cache", "backups", "proposals"}

    def __init__(self, base_path):
        self.root = Path(base_path).resolve()
        self.directory = self.root / "backups"

    def _sources(self):
        for name in self.FILES:
            p = self.root / name
            if p.is_file() and not p.is_symlink():
                yield p
        for dirname in self.DIRECTORIES:
            directory = self.root / dirname
            if not directory.is_dir() or directory.is_symlink():
                continue
            for root, dirs, filenames in os.walk(directory, followlinks=False):
                dirs[:] = sorted(d for d in dirs if d not in self.SKIP_DIRS and not (Path(root) / d).is_symlink())
                for name in sorted(filenames):
                    p = Path(root) / name
                    if name.startswith(".env") or name in {"secrets.json"} or p.is_symlink():
                        continue
                    if p.suffix.lower() in self.ALLOWED and p.resolve().is_relative_to(self.root):
                        yield p

    def create_backup(self, reason="manual"):
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        archive_name = "bud_backup_{}_{}.zip".format(stamp, uuid.uuid4().hex[:10])
        temporary = None
        try:
            source_files = sorted(set(self._sources()))
            if not source_files:
                return {"success": False, "error": "Nenhum arquivo-fonte para backup"}
            self.directory.mkdir(parents=True, exist_ok=True)
            temporary = self.directory / (archive_name + ".tmp")
            final = self.directory / archive_name
            with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED) as zipped:
                for source in source_files:
                    zipped.write(source, source.relative_to(self.root).as_posix())
            with zipfile.ZipFile(temporary) as zipped:
                if zipped.testzip() is not None or len(zipped.namelist()) != len(source_files):
                    raise RuntimeError("Arquivo ZIP inválido ou incompleto")
            os.replace(temporary, final)
            return {
                "success": True,
                "backup_created": final.relative_to(self.root).as_posix(),
                "files_backed_up": len(source_files),
                "timestamp": stamp,
                "reason": reason,
            }
        except Exception as exc:
            return {"success": False, "error": "Falha real no backup: {}".format(exc)}
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()
