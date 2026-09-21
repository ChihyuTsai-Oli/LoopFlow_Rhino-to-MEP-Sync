# R2M-B01：在 Rhino 8／CPython 3.9 針刺 IfcOpenShell。
# 不寫入使用者正在編輯的文件；由 MCP 在隔離 slot 執行。

from __future__ import annotations

import os
import sys
import traceback

VENDOR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", ".vendor", "py39")
)
OUT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "fixtures", "spike")
)


def _ensure_vendor():
    if VENDOR not in sys.path:
        sys.path.insert(0, VENDOR)


def _guid(ifcopenshell):
    return ifcopenshell.guid.new()


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


def _placement3d(ifc, x, y, z, axis=None, ref=None):
    kwargs = {"Location": _point(ifc, x, y, z)}
    if axis is not None:
        kwargs["Axis"] = _dir(ifc, *axis)
    if ref is not None:
        kwargs["RefDirection"] = _dir(ifc, *ref)
    return ifc.create_entity("IfcAxis2Placement3D", **kwargs)


def _local(ifc, relative_to, x, y, z, axis=None, ref=None):
    return ifc.create_entity(
        "IfcLocalPlacement",
        PlacementRelTo=relative_to,
        RelativePlacement=_placement3d(ifc, x, y, z, axis, ref),
    )


def _body_rep(ifc, context, item, rep_type="SweptSolid"):
    shape = ifc.create_entity(
        "IfcShapeRepresentation",
        ContextOfItems=context,
        RepresentationIdentifier="Body",
        RepresentationType=rep_type,
        Items=[item],
    )
    return ifc.create_entity("IfcProductDefinitionShape", Representations=[shape])


# 立方體的十二個三角形，索引對應 _box_mesh 的八個角點順序，法線朝外。
_BOX_TRIANGLES = (
    (0, 2, 1), (0, 3, 2),  # 底
    (4, 5, 6), (4, 6, 7),  # 頂
    (0, 1, 5), (0, 5, 4),  # -Y
    (1, 2, 6), (1, 6, 5),  # +X
    (2, 3, 7), (2, 7, 6),  # +Y
    (3, 0, 4), (3, 4, 7),  # -X
)


def _box_mesh_rep(ifc, context, x0, y0, z0, x1, y1, z1):
    """把一個軸對齊立方體寫成 IfcTriangulatedFaceSet。

    這是產品實際會用的幾何表示法：任意 Rhino 幾何先轉網面再三角化，
    不走參數化量體。座標是世界座標，所以元件本身用原點放置。
    """
    corners = (
        (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
        (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1),
    )
    points = ifc.create_entity(
        "IfcCartesianPointList3D",
        CoordList=[tuple(float(v) for v in c) for c in corners],
    )
    face_set = ifc.create_entity(
        "IfcTriangulatedFaceSet",
        Coordinates=points,
        Closed=True,
        # IFC 的索引從 1 起算
        CoordIndex=[tuple(i + 1 for i in tri) for tri in _BOX_TRIANGLES],
    )
    return _body_rep(ifc, context, face_set, rep_type="Tessellation")


def write_shell_mesh_ifc(path):
    """三角網面版建築殼，幾何與 write_shell_ifc 等價，供 BIM 端驗證用。"""
    import ifcopenshell
    import ifcopenshell.template

    ifc = ifcopenshell.template.create(
        filename=os.path.basename(path),
        organization="LoopFlow",
        creator="R2M spike",
        project_name="R2M-B03 shell (mesh)",
        application="LoopFlow R2M spike",
        application_version="0.0.0",
    )
    owner, context, storey = _spatial_tree(ifc, ifcopenshell)
    origin = _local(ifc, storey.ObjectPlacement, 0.0, 0.0, 0.0)
    wall = ifc.create_entity(
        "IfcWall",
        GlobalId=_guid(ifcopenshell),
        OwnerHistory=owner,
        Name="SpikeWall",
        ObjectPlacement=origin,
        Representation=_box_mesh_rep(ifc, context, 0.0, 0.0, 0.0, 4.0, 0.2, 2.8),
        PredefinedType="NOTDEFINED",
    )
    covering = ifc.create_entity(
        "IfcCovering",
        GlobalId=_guid(ifcopenshell),
        OwnerHistory=owner,
        Name="SpikeCeiling",
        ObjectPlacement=_local(ifc, storey.ObjectPlacement, 0.0, 0.0, 0.0),
        Representation=_box_mesh_rep(ifc, context, 0.0, 0.0, 2.8, 4.0, 4.0, 2.9),
        PredefinedType="CEILING",
    )
    ifc.create_entity(
        "IfcRelContainedInSpatialStructure",
        GlobalId=_guid(ifcopenshell),
        OwnerHistory=owner,
        RelatingStructure=storey,
        RelatedElements=[wall, covering],
    )
    ifc.write(path)
    return {
        "path": path,
        "schema": ifc.schema,
        "wall": wall.GlobalId,
        "covering": covering.GlobalId,
        "entity_count": len(list(ifc)),
    }


def _spatial_tree(ifc, ifcopenshell):
    owner = ifc.by_type("IfcOwnerHistory")[0]
    context = ifc.by_type("IfcGeometricRepresentationContext")[0]
    project = ifc.by_type("IfcProject")[0]
    world = _local(ifc, None, 0, 0, 0)
    site = ifc.create_entity(
        "IfcSite",
        GlobalId=_guid(ifcopenshell),
        OwnerHistory=owner,
        Name="SpikeSite",
        ObjectPlacement=world,
        CompositionType="ELEMENT",
    )
    building = ifc.create_entity(
        "IfcBuilding",
        GlobalId=_guid(ifcopenshell),
        OwnerHistory=owner,
        Name="SpikeBuilding",
        ObjectPlacement=_local(ifc, world, 0, 0, 0),
        CompositionType="ELEMENT",
    )
    storey = ifc.create_entity(
        "IfcBuildingStorey",
        GlobalId=_guid(ifcopenshell),
        OwnerHistory=owner,
        Name="Level 1",
        ObjectPlacement=_local(ifc, building.ObjectPlacement, 0, 0, 0),
        CompositionType="ELEMENT",
        Elevation=0.0,
    )
    ifc.create_entity(
        "IfcRelAggregates",
        GlobalId=_guid(ifcopenshell),
        OwnerHistory=owner,
        RelatingObject=project,
        RelatedObjects=[site],
    )
    ifc.create_entity(
        "IfcRelAggregates",
        GlobalId=_guid(ifcopenshell),
        OwnerHistory=owner,
        RelatingObject=site,
        RelatedObjects=[building],
    )
    ifc.create_entity(
        "IfcRelAggregates",
        GlobalId=_guid(ifcopenshell),
        OwnerHistory=owner,
        RelatingObject=building,
        RelatedObjects=[storey],
    )
    return owner, context, storey


def _rect_extrusion(ifc, context, xdim, ydim, depth):
    profile_place = ifc.create_entity(
        "IfcAxis2Placement2D",
        Location=ifc.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0)),
    )
    profile = ifc.create_entity(
        "IfcRectangleProfileDef",
        ProfileType="AREA",
        ProfileName=None,
        Position=profile_place,
        XDim=float(xdim),
        YDim=float(ydim),
    )
    solid = ifc.create_entity(
        "IfcExtrudedAreaSolid",
        SweptArea=profile,
        Position=_placement3d(ifc, 0, 0, 0),
        ExtrudedDirection=_dir(ifc, 0, 0, 1),
        Depth=float(depth),
    )
    return _body_rep(ifc, context, solid)


def _circle_extrusion(ifc, context, radius, depth):
    profile_place = ifc.create_entity(
        "IfcAxis2Placement2D",
        Location=ifc.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0)),
    )
    profile = ifc.create_entity(
        "IfcCircleProfileDef",
        ProfileType="AREA",
        ProfileName=None,
        Position=profile_place,
        Radius=float(radius),
    )
    solid = ifc.create_entity(
        "IfcExtrudedAreaSolid",
        SweptArea=profile,
        Position=_placement3d(ifc, 0, 0, 0, axis=(1, 0, 0), ref=(0, 1, 0)),
        ExtrudedDirection=_dir(ifc, 0, 0, 1),
        Depth=float(depth),
    )
    return _body_rep(ifc, context, solid)


def write_shell_ifc(path):
    import ifcopenshell
    import ifcopenshell.template

    ifc = ifcopenshell.template.create(
        filename=os.path.basename(path),
        organization="LoopFlow",
        creator="R2M spike",
        project_name="R2M-B01 shell",
        application="LoopFlow R2M spike",
        application_version="0.0.0",
    )
    owner, context, storey = _spatial_tree(ifc, ifcopenshell)
    wall = ifc.create_entity(
        "IfcWall",
        GlobalId=_guid(ifcopenshell),
        OwnerHistory=owner,
        Name="SpikeWall",
        ObjectPlacement=_local(ifc, storey.ObjectPlacement, 2.0, 0.1, 0.0),
        Representation=_rect_extrusion(ifc, context, 4.0, 0.2, 2.8),
        PredefinedType="NOTDEFINED",
    )
    covering = ifc.create_entity(
        "IfcCovering",
        GlobalId=_guid(ifcopenshell),
        OwnerHistory=owner,
        Name="SpikeCeiling",
        ObjectPlacement=_local(ifc, storey.ObjectPlacement, 2.0, 2.0, 2.8),
        Representation=_rect_extrusion(ifc, context, 4.0, 4.0, 0.1),
        PredefinedType="CEILING",
    )
    ifc.create_entity(
        "IfcRelContainedInSpatialStructure",
        GlobalId=_guid(ifcopenshell),
        OwnerHistory=owner,
        RelatingStructure=storey,
        RelatedElements=[wall, covering],
    )
    ifc.write(path)
    return {
        "path": path,
        "schema": ifc.schema,
        "wall": wall.GlobalId,
        "covering": covering.GlobalId,
        "entity_count": len(list(ifc)),
    }


def write_pipe_ifc(path):
    import ifcopenshell
    import ifcopenshell.template

    ifc = ifcopenshell.template.create(
        filename=os.path.basename(path),
        organization="LoopFlow",
        creator="R2M spike",
        project_name="R2M-B01 pipe",
        application="LoopFlow R2M spike",
        application_version="0.0.0",
    )
    owner, context, storey = _spatial_tree(ifc, ifcopenshell)
    pipe = ifc.create_entity(
        "IfcPipeSegment",
        GlobalId=_guid(ifcopenshell),
        OwnerHistory=owner,
        Name="SpikePipe",
        ObjectPlacement=_local(
            ifc, storey.ObjectPlacement, 0.0, 2.0, 2.5, axis=(1, 0, 0), ref=(0, 1, 0)
        ),
        Representation=_circle_extrusion(ifc, context, 0.075, 4.0),
        PredefinedType="NOTDEFINED",
    )
    ifc.create_entity(
        "IfcRelContainedInSpatialStructure",
        GlobalId=_guid(ifcopenshell),
        OwnerHistory=owner,
        RelatingStructure=storey,
        RelatedElements=[pipe],
    )
    ifc.write(path)
    return {
        "path": path,
        "schema": ifc.schema,
        "pipe": pipe.GlobalId,
        "entity_count": len(list(ifc)),
    }


def tessellate_to_rhino(doc, ifc_path, layer_path, metres_to_doc):
    import ifcopenshell
    import ifcopenshell.geom
    import Rhino
    import Rhino.Geometry as rg

    layer_index = _ensure_layer(doc, layer_path)
    model = ifcopenshell.open(ifc_path)
    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)
    added = []
    iterator = ifcopenshell.geom.iterator(settings, model)
    if not iterator.initialize():
        return {"ok": False, "reason": "geom iterator failed to initialize", "added": []}
    while True:
        shape = iterator.get()
        geom = shape.geometry
        verts = geom.verts
        faces = geom.faces
        mesh = rg.Mesh()
        zs = []
        for i in range(0, len(verts), 3):
            x = verts[i] * metres_to_doc
            y = verts[i + 1] * metres_to_doc
            z = verts[i + 2] * metres_to_doc
            mesh.Vertices.Add(x, y, z)
            zs.append(z)
        for i in range(0, len(faces), 3):
            mesh.Faces.AddFace(int(faces[i]), int(faces[i + 1]), int(faces[i + 2]))
        mesh.Normals.ComputeNormals()
        attr = Rhino.DocObjects.ObjectAttributes()
        attr.LayerIndex = layer_index
        attr.Name = "{}:{}".format(shape.type, shape.guid)
        oid = doc.Objects.AddMesh(mesh, attr)
        locked = bool(doc.Objects.Lock(oid, True))
        obj = doc.Objects.FindId(oid)
        bbox = mesh.GetBoundingBox(True)
        added.append(
            {
                "id": str(oid),
                "ifc_type": shape.type,
                "guid": shape.guid,
                "verts": mesh.Vertices.Count,
                "faces": mesh.Faces.Count,
                "zmin": bbox.Min.Z,
                "zmax": bbox.Max.Z,
                "locked": locked and (bool(obj.IsLocked) if obj is not None else True),
            }
        )
        if not iterator.next():
            break
    return {"ok": True, "added": added}


def _ensure_layer(doc, full_path):
    from Rhino.DocObjects import Layer

    existing = doc.Layers.FindByFullPath(full_path, -1)
    if existing >= 0:
        return existing
    parts = full_path.split("::")
    parent_index = -1
    built = []
    for part in parts:
        built.append(part)
        path = "::".join(built)
        found = doc.Layers.FindByFullPath(path, -1)
        if found >= 0:
            parent_index = found
            continue
        lyr = Layer()
        lyr.Name = part
        if parent_index >= 0:
            lyr.ParentLayerId = doc.Layers[parent_index].Id
        parent_index = doc.Layers.Add(lyr)
    return parent_index


def _cycles_status():
    import Rhino

    found = []
    mapping = Rhino.PlugIns.PlugIn.GetInstalledPlugIns()
    for guid in mapping.Keys:
        name = mapping[guid]
        if "cycle" in name.lower() or "raytrac" in name.lower():
            loaded = Rhino.PlugIns.PlugIn.LoadPlugIn(guid)
            found.append({"name": name, "guid": str(guid), "load_ok": bool(loaded)})
    return found


def run(doc):
    import Rhino

    _ensure_vendor()
    os.makedirs(OUT_DIR, exist_ok=True)
    report = {
        "python": sys.version,
        "rhino": str(Rhino.RhinoApp.Version),
        "units": str(doc.ModelUnitSystem),
        "vendor": VENDOR,
    }
    try:
        import ifcopenshell
        import ifcopenshell.geom

        report["import_ok"] = True
        report["ifcopenshell"] = ifcopenshell.version
    except Exception as exc:
        report["import_ok"] = False
        report["import_error"] = "{}: {}".format(type(exc).__name__, exc)
        report["traceback"] = traceback.format_exc()
        return report

    metres_to_doc = 1.0 / Rhino.RhinoMath.UnitScale(
        doc.ModelUnitSystem, Rhino.UnitSystem.Meters
    )
    report["metres_to_doc"] = metres_to_doc
    for obj in list(doc.Objects):
        doc.Objects.Unlock(obj.Id, True)
        doc.Objects.Delete(obj.Id, True)
    report["cleared_template"] = True
    report["cycles_before"] = _cycles_status()

    shell_path = os.path.join(OUT_DIR, "R2M_spike_shell.ifc")
    pipe_path = os.path.join(OUT_DIR, "R2M_spike_pipe.ifc")
    report["shell"] = write_shell_ifc(shell_path)
    report["pipe"] = write_pipe_ifc(pipe_path)
    report["shell_import"] = tessellate_to_rhino(
        doc, shell_path, "R2M::Shell", metres_to_doc
    )
    report["pipe_import"] = tessellate_to_rhino(
        doc, pipe_path, "R2M::Ref", metres_to_doc
    )
    report["cycles_after"] = _cycles_status()

    if report["pipe_import"].get("ok") and report["shell_import"].get("ok"):
        pipe_z = [item["zmax"] for item in report["pipe_import"]["added"]]
        ceil_z = [
            item["zmin"]
            for item in report["shell_import"]["added"]
            if item["ifc_type"] == "IfcCovering"
        ]
        if pipe_z and ceil_z:
            report["clearance_doc_units"] = min(ceil_z) - max(pipe_z)
    return report


def run_mesh_fixture(doc):
    """只產生三角網面版建築殼並讀回 Rhino 驗證，不重跑整套針刺。"""
    import Rhino

    _ensure_vendor()
    os.makedirs(OUT_DIR, exist_ok=True)
    metres_to_doc = 1.0 / Rhino.RhinoMath.UnitScale(
        doc.ModelUnitSystem, Rhino.UnitSystem.Meters
    )
    for obj in list(doc.Objects):
        doc.Objects.Unlock(obj.Id, True)
        doc.Objects.Delete(obj.Id, True)
    path = os.path.join(OUT_DIR, "R2M_spike_shell_mesh.ifc")
    report = {
        "units": str(doc.ModelUnitSystem),
        "metres_to_doc": metres_to_doc,
        "write": write_shell_mesh_ifc(path),
    }
    report["read_back"] = tessellate_to_rhino(doc, path, "R2M::Shell", metres_to_doc)
    return report


if __name__ == "__main__":
    doc = globals().get("__rhino_doc__")
    if doc is None:
        raise SystemExit("必須在 Rhino MCP run_python 執行")
    result = run(doc)
    import json

    print(json.dumps(result, indent=2, ensure_ascii=False))
