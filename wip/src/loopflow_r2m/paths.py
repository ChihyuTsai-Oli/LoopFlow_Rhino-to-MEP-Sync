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


def public_docs_dir(anchor):
    """公開說明資料夾。開發期是 repo 根 `docs/`；yak 是套件內 `docs/`。"""
    here = Path(anchor).resolve()
    candidates = []
    if len(here.parents) > 3:
        candidates.append(here.parents[3] / "docs")
    if len(here.parents) > 4:
        candidates.append(here.parents[4] / "docs")
    for folder in candidates:
        if (folder / "README.md").is_file():
            return folder
    if len(here.parents) > 4:
        return here.parents[4] / "docs"
    raise RuntimeError("找不到公開 docs/")


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
