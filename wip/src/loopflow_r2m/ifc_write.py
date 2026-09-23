"""把三角網面產品寫成 IFC4 Tessellation。不 import Rhino。

XY 維持 Rhino 世界座標。樓層 ObjectPlacement 的 Z 用 FL（公尺）；
網面頂點 Z 改成相對該層框的幾何高度，BIM 合成後＝FL + (世界Z − 框Z)。
"""

from __future__ import annotations

from collections import namedtuple

from .guid import compress_guid
from .names import PRODUCER


class ExportStorey(namedtuple("_ExportStorey", "name elevation_m frame_z_m")):
    """elevation_m 是 FL；frame_z_m 是框的幾何高度（皆公尺）。省略框高則視為等於 FL。"""

    def __new__(cls, name, elevation_m, frame_z_m=None):
        fl = float(elevation_m)
        hang = fl if frame_z_m is None else float(frame_z_m)
        return super(ExportStorey, cls).__new__(cls, name, fl, hang)


ExportProduct = namedtuple(
    "ExportProduct", "ifc_type global_id name storey_name vertices faces"
)
ExportMeta = namedtuple(
    "ExportMeta",
    "filename project_name site_name building_name product_version",
)


def _point(ifc, x, y, z=0.0):
    return ifc.create_entity(
        "IfcCartesianPoint", Coordinates=(float(x), float(y), float(z))
    )


def _dir(ifc, x, y, z=None):
    if z is None:
        return ifc.create_entity("IfcDirection", DirectionRatios=(float(x), float(y)))
    return ifc.create_entity(
        "IfcDirection", DirectionRatios=(float(x), float(y), float(z))
    )


def _placement3d(ifc, x, y, z):
    return ifc.create_entity(
        "IfcAxis2Placement3D",
        Location=_point(ifc, x, y, z),
        Axis=_dir(ifc, 0, 0, 1),
        RefDirection=_dir(ifc, 1, 0, 0),
    )


def _local(ifc, relative_to, x, y, z):
    return ifc.create_entity(
        "IfcLocalPlacement",
        PlacementRelTo=relative_to,
        RelativePlacement=_placement3d(ifc, x, y, z),
    )


def _stable_guid(seed):
    import hashlib

    digest = hashlib.md5(seed.encode("utf-8")).hexdigest()
    return compress_guid(digest)


def relative_vertices(vertices, frame_z_m):
    """世界座標頂點改成相對該層框：XY 不變，Z 減去框高。"""
    z0 = float(frame_z_m)
    out = []
    for xyz in vertices:
        x, y, z = xyz
        out.append((float(x), float(y), float(z) - z0))
    return out


def ordered_storeys(storeys):
    """依 FL 由低到高，讓 BIM 導覽器順序對得上。"""
    return sorted(storeys, key=lambda item: (float(item.elevation_m), item.name))


def _spatial(ifc, ifcopenshell, meta, storeys):
    owner = ifc.by_type("IfcOwnerHistory")[0]
    context = ifc.by_type("IfcGeometricRepresentationContext")[0]
    project = ifc.by_type("IfcProject")[0]
    project.Name = meta.project_name
    world = _local(ifc, None, 0, 0, 0)
    site = ifc.create_entity(
        "IfcSite",
        GlobalId=_stable_guid("site:" + meta.site_name),
        OwnerHistory=owner,
        Name=meta.site_name,
        ObjectPlacement=world,
        CompositionType="ELEMENT",
    )
    building = ifc.create_entity(
        "IfcBuilding",
        GlobalId=_stable_guid("building:" + meta.building_name),
        OwnerHistory=owner,
        Name=meta.building_name,
        ObjectPlacement=_local(ifc, world, 0, 0, 0),
        CompositionType="ELEMENT",
    )
    storey_map = {}
    storey_entities = []
    for storey in ordered_storeys(storeys):
        elev = float(storey.elevation_m)
        entity = ifc.create_entity(
            "IfcBuildingStorey",
            GlobalId=_stable_guid("storey:%s:%s" % (storey.name, elev)),
            OwnerHistory=owner,
            Name=storey.name,
            ObjectPlacement=_local(ifc, building.ObjectPlacement, 0, 0, elev),
            CompositionType="ELEMENT",
            Elevation=elev,
        )
        storey_map[storey.name] = entity
        storey_entities.append(entity)
    ifc.create_entity(
        "IfcRelAggregates",
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=owner,
        RelatingObject=project,
        RelatedObjects=[site],
    )
    ifc.create_entity(
        "IfcRelAggregates",
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=owner,
        RelatingObject=site,
        RelatedObjects=[building],
    )
    ifc.create_entity(
        "IfcRelAggregates",
        GlobalId=ifcopenshell.guid.new(),
        OwnerHistory=owner,
        RelatingObject=building,
        RelatedObjects=storey_entities,
    )
    return owner, context, storey_map


def _tessellation(ifc, context, vertices, faces):
    points = ifc.create_entity(
        "IfcCartesianPointList3D",
        CoordList=[tuple(float(v) for v in xyz) for xyz in vertices],
    )
    face_set = ifc.create_entity(
        "IfcTriangulatedFaceSet",
        Coordinates=points,
        CoordIndex=[tuple(int(i) + 1 for i in tri) for tri in faces],
    )
    shape = ifc.create_entity(
        "IfcShapeRepresentation",
        ContextOfItems=context,
        RepresentationIdentifier="Body",
        RepresentationType="Tessellation",
        Items=[face_set],
    )
    return ifc.create_entity("IfcProductDefinitionShape", Representations=[shape])


def write_models_ifc(path, meta, storeys, products):
    """寫出建築殼 IFC。長度已是公尺。XY 世界座標；Z 相對樓層框。"""
    import ifcopenshell
    import ifcopenshell.template

    if not storeys:
        raise ValueError("no storeys")
    if not products:
        raise ValueError("no products")

    ifc = ifcopenshell.template.create(
        filename=meta.filename,
        organization="LoopFlow",
        creator=PRODUCER,
        project_name=meta.project_name,
        application=PRODUCER,
        application_version=meta.product_version,
        schema_identifier="IFC4",
    )
    owner, context, storey_map = _spatial(ifc, ifcopenshell, meta, storeys)
    frames = {item.name: item for item in storeys}
    grouped = {}
    extra = {"PredefinedType": "NOTDEFINED"}
    for product in products:
        storey = storey_map.get(product.storey_name)
        if storey is None:
            raise ValueError("unknown storey: %s" % product.storey_name)
        verts = relative_vertices(
            product.vertices, frames[product.storey_name].frame_z_m
        )
        kwargs = {
            "GlobalId": product.global_id,
            "OwnerHistory": owner,
            "Name": product.name,
            "ObjectPlacement": _local(ifc, storey.ObjectPlacement, 0.0, 0.0, 0.0),
            "Representation": _tessellation(ifc, context, verts, product.faces),
        }
        kwargs.update(extra)
        try:
            entity = ifc.create_entity(product.ifc_type, **kwargs)
        except Exception:
            kwargs.pop("PredefinedType", None)
            entity = ifc.create_entity(product.ifc_type, **kwargs)
        grouped.setdefault(product.storey_name, []).append(entity)
    for storey_name, elements in grouped.items():
        ifc.create_entity(
            "IfcRelContainedInSpatialStructure",
            GlobalId=ifcopenshell.guid.new(),
            OwnerHistory=owner,
            RelatingStructure=storey_map[storey_name],
            RelatedElements=elements,
        )
    ifc.write(path)
    return path
