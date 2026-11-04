"""Contratos de dados sintéticos/offline; nenhuma interface de execução de ordens."""
from .observer import SnapshotError, analyze_snapshot, load_snapshot

__all__ = ["SnapshotError", "analyze_snapshot", "load_snapshot"]
