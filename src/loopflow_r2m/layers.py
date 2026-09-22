"""圖層路徑與排除記號。"""

from .names import DEFAULT_EXCLUDE_TOKEN, LAYER_ROOT, STOREY_LAYER


def layer_is_excluded(layer_path, exclude_token=DEFAULT_EXCLUDE_TOKEN):
    """圖層路徑含排除記號則不匯出。空白記號＝不排除。"""
    token = "" if exclude_token is None else str(exclude_token).strip()
    if token == "":
        return False
    return token in str(layer_path)


def is_storey_layer_path(layer_path):
    """圖層 `R2M::Storey` 或其巢狀路徑。"""
    path = str(layer_path)
    return path == STOREY_LAYER or path.endswith("::" + STOREY_LAYER)


def is_r2m_system_layer_path(layer_path):
    """R2M 自己建的圖層樹（`R2M` 及其所有子層），整棵都不進匯出清單。"""
    parts = str(layer_path).split("::")
    return LAYER_ROOT in parts


def is_leaf_layer_path(path, all_paths):
    """沒有任何路徑以 `path::` 開頭，才是最末端圖層。"""
    prefix = str(path) + "::"
    for other in all_paths:
        if str(other).startswith(prefix):
            return False
    return True


def filter_leaf_layer_rows(rows):
    """只留最末端圖層列。父層即使有物件也不列出。"""
    rows = list(rows or [])
    paths = [row["path"] for row in rows]
    return [row for row in rows if is_leaf_layer_path(row["path"], paths)]
