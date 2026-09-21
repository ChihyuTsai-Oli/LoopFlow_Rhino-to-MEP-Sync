"""pending IFC 的六項發布驗證。"""

from __future__ import annotations

SPATIAL = {
    "IfcProject",
    "IfcSite",
    "IfcBuilding",
    "IfcBuildingStorey",
    "IfcSpace",
}


class ValidateError(ValueError):
    """驗證失敗，應保留 last-good。"""


def validate_models_ifc(path, expected_count):
    import ifcopenshell

    try:
        ifc = ifcopenshell.open(str(path))
    except Exception as exc:
        raise ValidateError("cannot reopen pending IFC: %s" % exc) from exc
    if ifc.schema != "IFC4":
        raise ValidateError("schema is %s, expected IFC4" % ifc.schema)
    if len(list(ifc)) == 0:
        raise ValidateError("IFC has no entities")
    for required in ("IfcProject", "IfcSite", "IfcBuilding", "IfcBuildingStorey"):
        if not ifc.by_type(required):
            raise ValidateError("missing %s" % required)
    elements = [
        item
        for item in ifc.by_type("IfcProduct")
        if item.is_a() not in SPATIAL
    ]
    if len(elements) != int(expected_count):
        raise ValidateError(
            "element count %s != expected %s" % (len(elements), expected_count)
        )
    related = set()
    for rel in ifc.by_type("IfcRelContainedInSpatialStructure"):
        for item in rel.RelatedElements or []:
            related.add(item.id())
    orphans = [item for item in elements if item.id() not in related]
    if orphans:
        raise ValidateError("%s elements are not on a storey" % len(orphans))
    xs, ys, zs = [], [], []
    for listing in ifc.by_type("IfcCartesianPointList3D"):
        for xyz in listing.CoordList or []:
            xs.append(float(xyz[0]))
            ys.append(float(xyz[1]))
            zs.append(float(xyz[2]))
    if not xs:
        raise ValidateError("empty geometry bounds")
    if min(xs) == max(xs) and min(ys) == max(ys) and min(zs) == max(zs):
        raise ValidateError("degenerate geometry bounds")
    return {
        "schema": ifc.schema,
        "elements": len(elements),
        "storeys": len(ifc.by_type("IfcBuildingStorey")),
    }
