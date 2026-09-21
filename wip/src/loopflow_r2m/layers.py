"""圖層路徑與排除記號。"""

from .names import DEFAULT_EXCLUDE_TOKEN


def layer_is_excluded(layer_path, exclude_token=DEFAULT_EXCLUDE_TOKEN):
    """圖層路徑含排除記號則不匯出。空白記號＝不排除。"""
    token = "" if exclude_token is None else str(exclude_token)
    if token == "":
        return False
    return token in str(layer_path)
