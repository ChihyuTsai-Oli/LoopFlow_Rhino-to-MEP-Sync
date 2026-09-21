"""config.json 讀寫。未知 schema_version 即停，不猜測。"""

from __future__ import annotations

import json
from pathlib import Path

from .names import DEFAULT_MESH_DENSITY, MESH_DENSITIES, PRODUCER, SCHEMA_VERSION


class ConfigError(ValueError):
    """設定無法使用。"""


def default_config(document_name="", product_version="0.0.0-dev"):
    """新專案的預設物件。專案／基地／建築名預設取檔名。"""
    stem = Path(document_name).stem if document_name else ""
    return {
        "schema_version": SCHEMA_VERSION,
        "producer": PRODUCER,
        "product_version": product_version,
        "document_name": document_name,
        "project_name": stem,
        "site_name": stem,
        "building_name": stem,
        "last_export": None,
        "layer_selection": {},
        "layer_type_map": {},
        "mesh_density": DEFAULT_MESH_DENSITY,
        "inbound_count_warning": None,
    }


def load_config(path):
    """讀 JSON。未知 schema 或不是物件則丟 ConfigError。"""
    text = Path(path).read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ConfigError("config.json 無法解析") from exc
    if not isinstance(data, dict):
        raise ConfigError("config.json 必須是單一物件")
    version = data.get("schema_version")
    if version != SCHEMA_VERSION:
        raise ConfigError("未知 schema_version：%s" % version)
    density = data.get("mesh_density", DEFAULT_MESH_DENSITY)
    if density not in MESH_DENSITIES:
        raise ConfigError("未知 mesh_density：%s" % density)
    return data


def save_config(path, data):
    """以 UTF-8 寫出，結尾換行。"""
    if not isinstance(data, dict):
        raise ConfigError("config 必須是物件")
    if data.get("schema_version") != SCHEMA_VERSION:
        raise ConfigError("未知 schema_version：%s" % data.get("schema_version"))
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    target.write_text(payload, encoding="utf-8")
