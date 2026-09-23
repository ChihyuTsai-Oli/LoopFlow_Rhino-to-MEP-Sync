"""設定根的英文 Health 摘要。不 import Rhino。"""

from __future__ import annotations

from pathlib import Path

from .config import ConfigError, load_config


def health_lines(paths, config=None):
    """回傳給 RMOpen 顯示的英文行。"""
    root = Path(paths["root"])
    config_path = Path(paths["config"])
    log_path = Path(paths["log"])
    ifc_path = Path(paths["ifc"])
    lines = [
        "Config root: %s" % root.name,
        "config.json: %s" % ("yes" if config_path.is_file() else "missing"),
        "last-good IFC: %s" % ("yes" if ifc_path.is_file() else "missing"),
        "log: %s" % ("yes" if log_path.is_file() else "missing"),
    ]
    data = config
    if data is None and config_path.is_file():
        try:
            data = load_config(config_path)
        except ConfigError as exc:
            lines.append("config error: %s" % exc)
            return lines
    if data:
        last = data.get("last_export") or {}
        lines.append("project: %s" % (data.get("project_name") or "(none)"))
        if last:
            lines.append(
                "last export: %s objects, %s storeys, %s"
                % (
                    last.get("object_count", "?"),
                    last.get("storey_count", "?"),
                    last.get("timestamp", "?"),
                )
            )
            lines.append("ifc: %s" % (last.get("ifc_path") or ifc_path.name))
        else:
            lines.append("last export: none")
    if ifc_path.is_file():
        lines.append("ifc size: %s bytes" % ifc_path.stat().st_size)
    return lines
