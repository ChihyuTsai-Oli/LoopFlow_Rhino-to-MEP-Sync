"""R2M 已決的機器名稱。指令名仍未凍結；這些是資料契約裡的圖層／欄位名。"""

LAYER_ROOT = "R2M"
STOREY_LAYER = LAYER_ROOT + "::Storey"
STOREY_NAME_KEY = "R2M_StoreyName"
STOREY_FL_KEY = "R2M_FL"
DEFAULT_EXCLUDE_TOKEN = "//"
PRODUCER = "LoopFlow R2M"
PRODUCT_VERSION = "0.0.0-dev"
SCHEMA_VERSION = "1"
DEFAULT_MESH_DENSITY = "medium"
MESH_DENSITIES = ("coarse", "medium", "fine")
CONFIG_FOLDER = "_LoopFlow_Config"
CONFIG_PRODUCT = "loopflow_R2M"
MODELS_IFC_NAME = "R2M.ifc"
PENDING_IFC_NAME = "R2M.pending.ifc"
LOG_NAME = "r2m.log"
CONFIG_NAME = "config.json"
INBOUND_LAYER_ROOT = "R2M_Inbound"
INBOUND_COUNT_WARNING_KEY = "inbound_count_warning"
ELEVATION_SHIFT_KEY = "elevation_shift"

# 未選＝IfcPlate（泛用板件，Archicad 較可能顯示）。天花請明示 IfcCovering。
# 不下 IfcCeiling（IFC4 無此產品類）。舊預設 Proxy 讀回來當未選。
DEFAULT_IFC_TYPE = "IfcPlate"
LEGACY_DEFAULT_IFC_TYPE = "IfcBuildingElementProxy"
IFC_PRODUCT_TYPES = (
    "IfcWall",
    "IfcCovering",
    "IfcSlab",
    "IfcRoof",
    "IfcColumn",
    "IfcBeam",
    "IfcCurtainWall",
    "IfcDoor",
    "IfcWindow",
    "IfcRailing",
    "IfcStair",
    "IfcRamp",
    "IfcPlate",
    "IfcMember",
    LEGACY_DEFAULT_IFC_TYPE,
)


def ifc_type_choices():
    """下拉順序：預設 Plate 在最前，其餘維持契約表順序。"""
    rest = [name for name in IFC_PRODUCT_TYPES if name != DEFAULT_IFC_TYPE]
    return (DEFAULT_IFC_TYPE,) + tuple(rest)


# 相對公差無單位；最小邊長以公尺計，寫入 Rhino 時再換成文件單位。
MESH_RELATIVE_TOLERANCE = {"coarse": 0.8, "medium": 0.4, "fine": 0.15}
MESH_MIN_EDGE_METERS = {"coarse": 0.05, "medium": 0.02, "fine": 0.005}

GEOM_CLASSES = (
    ("brep", "Brep", True),
    ("extrusion", "Extrusion", True),
    ("mesh", "Mesh", True),
    ("subd", "SubD", True),
    ("surface", "Surface", True),
    ("hatch", "Hatch", True),
    ("curve", "Curve", False),
    ("point", "Point", False),
)
