"""圖層路徑與排除記號。"""

from .names import DEFAULT_EXCLUDE_TOKEN, STOREY_LAYER


def layer_is_excluded(layer_path, exclude_token=DEFAULT_EXCLUDE_TOKEN):
    """圖層路徑含排除記號則不匯出。空白記號＝不排除。"""
    token = "" if exclude_token is None else str(exclude_token).strip()
    if token == "":
        return False
    return token in str(layer_path)


def is_storey_layer_path(layer_path):
    """圖層 `R2M_Storey` 或其巢狀路徑。"""
    path = str(layer_path)
    return path == STOREY_LAYER or path.endswith("::" + STOREY_LAYER)
