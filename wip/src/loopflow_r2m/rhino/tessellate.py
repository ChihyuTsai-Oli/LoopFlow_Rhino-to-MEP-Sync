"""把 IFC 產品建成鎖定網面，依類型分層上色。"""

from __future__ import annotations

from loopflow_r2m.exceptions import R2MStop
from loopflow_r2m.ifc_read import inbound_layer_color, inbound_layer_path, inbound_object_name
from loopflow_r2m.rhino.layerutil import ensure_layer
from loopflow_r2m.vendor import ensure_vendor


def tessellate_inbound(doc, ifc_path, metres_to_doc):
    """回傳 {success, failed, added}。不可初始化幾何迭代則停。"""
    import ifcopenshell
    import ifcopenshell.geom
    import Rhino
    import Rhino.Geometry as rg

    ensure_vendor()
    model = ifcopenshell.open(str(ifc_path))
    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)
    iterator = ifcopenshell.geom.iterator(settings, model)
    if not iterator.initialize():
        raise R2MStop("Cannot tessellate this IFC.")

    success = 0
    failed = 0
    added = []
    while True:
        shape = iterator.get()
        try:
            geom = shape.geometry
            verts = geom.verts
            faces = geom.faces
            mesh = rg.Mesh()
            for i in range(0, len(verts), 3):
                mesh.Vertices.Add(
                    verts[i] * metres_to_doc,
                    verts[i + 1] * metres_to_doc,
                    verts[i + 2] * metres_to_doc,
                )
            for i in range(0, len(faces), 3):
                mesh.Faces.AddFace(
                    int(faces[i]), int(faces[i + 1]), int(faces[i + 2])
                )
            mesh.Normals.ComputeNormals()
            if mesh.Vertices.Count < 3 or mesh.Faces.Count < 1:
                raise ValueError("empty mesh")
            ifc_type = shape.type
            guid = shape.guid
            layer_index = ensure_layer(
                doc, inbound_layer_path(ifc_type), inbound_layer_color(ifc_type)
            )
            attr = Rhino.DocObjects.ObjectAttributes()
            attr.LayerIndex = layer_index
            attr.Name = inbound_object_name(ifc_type, guid)
            oid = doc.Objects.AddMesh(mesh, attr)
            doc.Objects.Lock(oid, True)
            added.append(str(oid))
            success += 1
        except Exception:
            failed += 1
        if not iterator.next():
            break
    if success == 0:
        raise R2MStop("No meshable products in this IFC.")
    return {"success": success, "failed": failed, "added": added}
