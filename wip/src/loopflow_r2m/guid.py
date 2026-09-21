"""IFC GlobalId：把 Rhino GUID 的 32 字 hex（ToString('N')）壓成 22 字。

編碼慣例與 IfcOpenShell `guid.compress`／buildingSMART IFC GUID 相同，
實作不 import ifcopenshell，以便系統 Python 測試不必載入 numpy。
"""

from __future__ import annotations

import re
import string
from base64 import b64decode, b64encode

_CHARS64_STD = string.ascii_uppercase + string.ascii_lowercase + string.digits + "+/"
_CHARS64_IFC = string.digits + string.ascii_uppercase + string.ascii_lowercase + "_$"
_TRANS_STD_TO_IFC = str.maketrans(_CHARS64_STD, _CHARS64_IFC)
_TRANS_IFC_TO_STD = str.maketrans(_CHARS64_IFC, _CHARS64_STD)


def compress_guid(uuid_text):
    """把 hex UUID 壓成 22 字 IFC GlobalId。"""
    uuid_text = re.sub(r"\W", "", str(uuid_text).lower())
    if len(uuid_text) != 32:
        raise ValueError("GUID 必須是 32 字 hex（可含連字號）")
    padded = bytes.fromhex("0000" + uuid_text)
    guid = b64encode(padded).decode()[2:]
    return guid.translate(_TRANS_STD_TO_IFC)


def expand_guid(guid):
    """把 22 字 IFC GlobalId 還原成 32 字 hex。"""
    guid = str(guid)
    if len(guid) != 22:
        raise ValueError("IFC GlobalId 必須是 22 字")
    uuid_hex = b64decode("AA" + guid.translate(_TRANS_IFC_TO_STD)).hex()[4:]
    return uuid_hex
