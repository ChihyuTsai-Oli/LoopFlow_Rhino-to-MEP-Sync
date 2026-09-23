"""config.json 讀寫。未知 schema_version 即停，不猜測。"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

from .names import (
    DEFAULT_EXCLUDE_TOKEN,
    DEFAULT_MESH_DENSITY,
    MESH_DENSITIES,
    PRODUCER,
    SCHEMA_VERSION,
)


class ConfigError(ValueError):
    """設定無法使用。"""


_PANEL_WRITE_TRIES = 6
_PANEL_WRITE_WAIT = 0.25


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
        "panels": {},
        "mesh_density": DEFAULT_MESH_DENSITY,
        "inbound_count_warning": None,
        "elevation_shift": None,
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
    panels = data.get("panels")
    if panels is None:
        data["panels"] = {}
    elif not isinstance(panels, dict):
        raise ConfigError("panels 必須是物件")
    return data


def save_config(path, data):
    """以 UTF-8 寫出，結尾換行。先寫暫存再置換，占用時重試。"""
    if not isinstance(data, dict):
        raise ConfigError("config 必須是物件")
    if data.get("schema_version") != SCHEMA_VERSION:
        raise ConfigError("未知 schema_version：%s" % data.get("schema_version"))
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    tmp = target.with_name(target.name + ".tmp")
    tmp.write_text(payload, encoding="utf-8")
    last_error = None
    for _attempt in range(_PANEL_WRITE_TRIES):
        try:
            os.replace(str(tmp), str(target))
            return
        except OSError as exc:
            last_error = exc
            time.sleep(_PANEL_WRITE_WAIT)
    raise ConfigError("config.json 無法寫入（檔案可能被占用）") from last_error


def panel_from_choice(choice):
    """對話框快照轉成可寫入的面板物件。"""
    choice = choice or {}
    density = choice.get("mesh_density", DEFAULT_MESH_DENSITY)
    if density not in MESH_DENSITIES:
        density = DEFAULT_MESH_DENSITY
    return {
        "exclude_token": choice.get("exclude_token", DEFAULT_EXCLUDE_TOKEN),
        "layer_paths": list(choice.get("layer_paths") or []),
        "layer_type_map": dict(choice.get("layer_type_map") or {}),
        "geom": dict(choice.get("geom") or {}),
        "mesh_density": density,
    }


def _legacy_panel(config):
    saved_sel = config.get("layer_selection") or {}
    return {
        "exclude_token": saved_sel.get("exclude_token", DEFAULT_EXCLUDE_TOKEN),
        "layer_paths": list(saved_sel.get("layer_paths") or []),
        "layer_type_map": dict(config.get("layer_type_map") or {}),
        "geom": dict(saved_sel.get("geom") or {}),
        "mesh_density": config.get("mesh_density", DEFAULT_MESH_DENSITY),
    }


def has_saved_panel(config, document_name):
    """這個 3dm 檔名是否已有面板紀錄。"""
    panels = config.get("panels") or {}
    if document_name in panels:
        return True
    if panels:
        return False
    saved_sel = config.get("layer_selection") or {}
    if not saved_sel.get("layer_paths") and not (config.get("layer_type_map") or {}):
        return False
    stored_name = config.get("document_name") or ""
    if stored_name and stored_name != document_name:
        return False
    return True


def panel_for(config, document_name):
    """讀這個 3dm 的面板。沒有分檔紀錄時，只在檔名對得上才沿用舊的頂層欄位。"""
    panels = config.get("panels") or {}
    if document_name in panels:
        return panel_from_choice(panels.get(document_name) or {})
    if has_saved_panel(config, document_name):
        return panel_from_choice(_legacy_panel(config))
    return panel_from_choice({})


def set_panel(config, document_name, choice):
    """寫入這個 3dm 的面板，並鏡像到頂層欄位（最後一次寫入）。"""
    panel = panel_from_choice(choice)
    panels = dict(config.get("panels") or {})
    panels[document_name] = panel
    config["panels"] = panels
    config["document_name"] = document_name
    config["layer_selection"] = {
        "exclude_token": panel["exclude_token"],
        "layer_paths": panel["layer_paths"],
        "geom": panel["geom"],
    }
    config["layer_type_map"] = panel["layer_type_map"]
    config["mesh_density"] = panel["mesh_density"]
    return config
