"""建立巢狀圖層。RMInbound 與 RMStorey 共用。"""

from __future__ import annotations


def ensure_layer(doc, full_path, rgb=None):
    """回傳圖層索引。沿路缺的父層一併建出；rgb 只套在最末層。"""
    from Rhino.DocObjects import Layer
    import System.Drawing

    def paint(layer):
        if rgb is None:
            return
        layer.Color = System.Drawing.Color.FromArgb(
            int(rgb[0]), int(rgb[1]), int(rgb[2])
        )

    existing = doc.Layers.FindByFullPath(full_path, -1)
    if existing >= 0:
        if rgb is not None:
            layer = doc.Layers[existing]
            paint(layer)
            doc.Layers.Modify(layer, existing, True)
        return existing

    parent_index = -1
    built = []
    index = -1
    for part in full_path.split("::"):
        built.append(part)
        path = "::".join(built)
        found = doc.Layers.FindByFullPath(path, -1)
        if found >= 0:
            parent_index = found
            index = found
            continue
        lyr = Layer()
        lyr.Name = part
        if parent_index >= 0:
            lyr.ParentLayerId = doc.Layers[parent_index].Id
        if path == full_path:
            paint(lyr)
        index = doc.Layers.Add(lyr)
        parent_index = index
    return index
