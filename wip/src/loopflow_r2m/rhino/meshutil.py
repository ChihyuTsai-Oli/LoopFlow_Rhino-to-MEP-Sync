"""Rhino 幾何轉三角網面，頂點換成公尺。"""

from __future__ import annotations

import math

from loopflow_r2m.names import MESH_MIN_EDGE_METERS, MESH_RELATIVE_TOLERANCE
from loopflow_r2m.units import meters_to_rhino, rhino_to_meters


def meshing_parameters(density, scale_to_meters):
    import Rhino

    try:
        mp = Rhino.Geometry.MeshingParameters.Default.Duplicate()
    except AttributeError:
        mp = Rhino.Geometry.MeshingParameters()
    mp.RelativeTolerance = MESH_RELATIVE_TOLERANCE[density]
    mp.MinimumEdgeLength = meters_to_rhino(
        MESH_MIN_EDGE_METERS[density], scale_to_meters
    )
    return mp


def geometry_to_mesh(geom, mp):
    import Rhino.Geometry as rg

    if geom is None:
        return None
    mesh = None
    if isinstance(geom, rg.Mesh):
        mesh = geom.DuplicateMesh()
    elif isinstance(geom, rg.Brep):
        parts = rg.Mesh.CreateFromBrep(geom, mp)
        if parts:
            mesh = rg.Mesh()
            for part in parts:
                mesh.Append(part)
    elif isinstance(geom, rg.Extrusion):
        brep = geom.ToBrep()
        return geometry_to_mesh(brep, mp)
    elif isinstance(geom, rg.Surface):
        brep = geom.ToBrep()
        return geometry_to_mesh(brep, mp)
    elif isinstance(geom, rg.SubD):
        try:
            mesh = rg.Mesh.CreateFromSubD(geom, 3)
        except TypeError:
            mesh = None
    elif isinstance(geom, rg.Hatch):
        try:
            breps = geom.CreateBrep()
        except Exception:
            breps = None
        if breps:
            mesh = rg.Mesh()
            for brep in breps:
                part = geometry_to_mesh(brep, mp)
                if part is not None:
                    mesh.Append(part)
    if mesh is None:
        return None
    mesh.Faces.ConvertQuadsToTriangles()
    mesh.Weld(math.radians(1.0))
    mesh.Normals.ComputeNormals()
    if mesh.Vertices.Count < 3 or mesh.Faces.Count < 1:
        return None
    return mesh


def mesh_to_meters(mesh, scale_to_meters):
    vertices = []
    for point in mesh.Vertices:
        vertices.append(
            (
                rhino_to_meters(point.X, scale_to_meters),
                rhino_to_meters(point.Y, scale_to_meters),
                rhino_to_meters(point.Z, scale_to_meters),
            )
        )
    faces = []
    for face in mesh.Faces:
        faces.append((int(face.A), int(face.B), int(face.C)))
    return vertices, faces
