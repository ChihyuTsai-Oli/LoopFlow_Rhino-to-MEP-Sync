# LoopFlow R2M User Guide

> Command names are frozen: `RMOpen`, `RMStorey`, `RMModels`, `RMInbound`. There is no Package Manager package yet; open the development toolbar for now. Dialogs are in English.
>
> One minute on how it works. Buttons and steps: [Commands](./COMMANDS.md). Product intro: [homepage](../README.md).

## Core idea: Rhino publishes the shell, BIM draws pipes, then attach them as a reference

**Design stays in Rhino.** There is no LoopFlow plug-in on the BIM side. Exchange is IFC only.

1. **Save the `.3dm` first.** Unpublished files cannot publish. Settings and exchange files sit next to that file.
2. **Register storeys, then publish the shell.** `RMStorey` names the frames; `RMModels` writes `models/R2M.ifc` (length unit: centimetres).
3. **Receive that IFC in BIM** (Archicad: File → Open as a new file; do not Merge. Revit: Link IFC, then create matching Levels and Floor Plans) and draw 3D geometry there. Heights in BIM follow the FL numbers you typed on the storey frames. Bonsai is another IFC working environment, like Revit and Archicad; this product **does not test Bonsai**.
4. **Bring the geometry IFC back (height correction).** BIM world coordinates are still building elevations. `RMInbound` shifts every vertex back onto the Rhino model — not onto the FL numbers — so inbound walls and pipes line up with the ceiling. You save and attach the Worksession yourself.
5. **Edit the original ceiling / wall / slab against the reference, then run Models again.**

No camera, lights, or live link. The tool does not continue to the next channel on its own.

## The project is a folder

The folder that holds the saved `.3dm` is the work folder. LoopFlow creates:

```text
_LoopFlow_Config/loopflow_R2M/
  models/      ← R2M.ifc (default product name; rename immediately if you keep whole-building and partial copies)
  inbound/     ← suggested place for the reference .3dm (not enforced, not auto-saved)
  config.json  ← includes elevation_shift from the last RMModels run
  r2m.log
```

A whole-building file and a partial-storey file in the same folder **share** this `config.json`. To inbound against the partial file, run `RMModels` on that file first so the correction value matches it (whole-building is usually 0).

Move the whole project folder when you change computers. The Worksession `.rws` is personal and is not stored inside the `.3dm`; re-attach it on the other machine. That is expected.

## How the two sides match

| You want to | Rhino | BIM |
|---|---|---|
| Register storeys | `RMStorey` | — |
| Architectural shell | `RMModels` | Archicad: **Open the IFC as a new file** (tested). Revit: **Link IFC**, then create matching Levels and Floor Plans (tested). Bonsai is an IFC working environment; **not tested** |
| Geometry reference (with height correction) | `RMInbound` → save by hand → attach Worksession by hand | BIM **IFC4** export, selected objects only. Archicad and Revit wall inbound heights have passed; real ducts/pipes are untested |
| Settings and docs | `RMOpen` | — |

BIM has no LoopFlow buttons.

## Terms

| Term | Meaning |
|---|---|
| **Storey frame** | A closed horizontal curve you draw, one per storey, at that storey’s height. It must sit **outside** the outer walls; touching the frame stops the publish. |
| **FL** | Structural-floor elevation. Do not enter FFL (finished floor). LoopFlow drawings use FFL; mixing them is about one finish thickness off. |
| **Height correction** | BIM draws to FL. The Rhino model often sits those floors at its own Z. `RMInbound` uses `elevation_shift` in `config.json` to pull inbound geometry back onto the model. |
| **Whole / partial** | `RMStorey` WholeBuilding or PartialStoreys. If you only modelled a few floors, do not invent 1F or RF. |
| **IfcPlate / IfcCovering** | Unset types write as Plate. Ceilings should be Covering. Proxy objects are often invisible in Archicad. |
| **Worksession reference** | After attach, inbound meshes are a reference you can snap to. `RMInbound` does **not** lock them. Models skips reference objects so pipes are not sent back to BIM. |

## Where it stops

- Unsaved file: `RMModels` / `RMOpen` stop. `RMStorey` / `RMInbound` do not require a saved file.
- Missing frames, duplicate names or FL, or storey height not matching the frames: no publish.
- Geometry that touches a frame edge: stop. Same-layer objects outside the frame: skip. Below the lowest frame: skip (the command line lists the count).
- Cancel, fail, or interrupt: the last good `R2M.ifc` is not overwritten. The source Rhino file returns to its previous state.
- Missing `elevation_shift` in `config.json`: `RMInbound` stops; it does not guess 0.

## How to click

This page is the logic. Paste lines, frames, and Archicad / Revit open: [Commands](./COMMANDS.md).
