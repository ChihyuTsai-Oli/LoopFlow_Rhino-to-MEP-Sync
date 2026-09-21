"""工作檔旁的 R2M 設定根。"""

from __future__ import annotations

from pathlib import Path

from .names import (
    CONFIG_FOLDER,
    CONFIG_NAME,
    CONFIG_PRODUCT,
    LOG_NAME,
    MODELS_IFC_NAME,
    PENDING_IFC_NAME,
)


def config_root(document_path):
    """`<3dm 資料夾>\\_LoopFlow_Config\\loopflow_R2M`。"""
    parent = Path(document_path).resolve().parent
    return parent / CONFIG_FOLDER / CONFIG_PRODUCT


def config_paths(document_path):
    root = config_root(document_path)
    models = root / "models"
    return {
        "root": root,
        "config": root / CONFIG_NAME,
        "log": root / LOG_NAME,
        "models": models,
        "ifc": models / MODELS_IFC_NAME,
        "pending": models / PENDING_IFC_NAME,
    }
