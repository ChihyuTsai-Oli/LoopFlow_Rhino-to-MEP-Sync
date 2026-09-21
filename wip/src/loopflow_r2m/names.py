"""R2M 已決的機器名稱。指令名仍未凍結；這些是資料契約裡的圖層／欄位名。"""

STOREY_LAYER = "R2M_Storey"
STOREY_NAME_KEY = "R2M_StoreyName"
STOREY_FL_KEY = "R2M_FL"
STOREY_FL_TOP_KEY = "R2M_FL_Top"
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

# 匯出時明確挑選；Proxy 必須使用者自己選，不得當缺省。
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
    "IfcBuildingElementProxy",
)

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
