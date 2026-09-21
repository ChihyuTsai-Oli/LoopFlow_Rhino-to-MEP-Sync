"""把三角網面產品寫成 IFC4 Tessellation。不 import Rhino。"""

from __future__ import annotations

from collections import namedtuple

from .guid import compress_guid
from .names import PRODUCER

ExportStorey = namedtuple("ExportStorey", "name elevation_m")
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
    for storey in storeys:
        entity = ifc.create_entity(
            "IfcBuildingStorey",
            GlobalId=_stable_guid("storey:%s:%s" % (storey.name, storey.elevation_m)),
            OwnerHistory=owner,
            Name=storey.name,
            ObjectPlacement=_local(ifc, building.ObjectPlacement, 0, 0, 0),
            CompositionType="ELEMENT",
            Elevation=float(storey.elevation_m),
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
    """寫出建築殼 IFC。座標已是公尺、世界座標。"""
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
    grouped = {}
    extra = {"PredefinedType": "NOTDEFINED"}
    for product in products:
        storey = storey_map.get(product.storey_name)
        if storey is None:
            raise ValueError("unknown storey: %s" % product.storey_name)
        kwargs = {
            "GlobalId": product.global_id,
            "OwnerHistory": owner,
            "Name": product.name,
            "ObjectPlacement": _local(ifc, storey.ObjectPlacement, 0.0, 0.0, 0.0),
            "Representation": _tessellation(
                ifc, context, product.vertices, product.faces
            ),
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
