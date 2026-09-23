# LoopFlow R2M User Guide

> **Development draft.** Command names are not frozen. There is no package or toolbar yet.
>
> One minute on how it works. Buttons and steps: [Commands](./COMMANDS.md). Product intro: [homepage](../README.md).

## Core idea: Rhino publishes the shell, BIM draws pipes, then lock them back as a reference

**Design stays in Rhino.** There is no LoopFlow plug-in on the BIM side. Exchange is IFC only.

1. **Save the `.3dm` first.** Unpublished files cannot publish. Settings and exchange files sit next to that file.
2. **Register storeys, then publish the shell.** `RMStorey` names the frames; `RMModels` writes `models/R2M.ifc`.
3. **Open that IFC as a new file in BIM** (Archicad: File → Open; do not Merge) and draw 3D pipes there. Heights in BIM follow the FL numbers you typed on the storey frames. Bonsai is another IFC working environment, like Revit and Archicad; this product **does not test Bonsai**.
4. **Bring the pipe IFC back.** `RMInbound` shifts Z back onto the Rhino model (not the building-elevation numbers). You save and attach the Worksession yourself.
5. **Edit the original ceiling / wall / slab against the reference, then run Models again.**

No camera, lights, or live link. The tool does not continue to the next channel on its own.

## The project is a folder

The folder that holds the saved `.3dm` is the work folder. LoopFlow creates:

```text
_LoopFlow_Config/loopflow_R2M/
  models/      ← R2M.ifc (default product name; keep copies if you export whole-building and partial files)
  inbound/     ← suggested place for the pipe .3dm (not enforced, not auto-saved)
  config.json
  r2m.log
```

Move the whole project folder when you change computers. The Worksession `.rws` is personal and is not stored inside the `.3dm`; re-attach it on the other machine. That is expected.

## How the two sides match

| You want to | Rhino | BIM |
|---|---|---|
| Register storeys | `RMStorey` | — |
| Architectural shell | `RMModels` | **Open the IFC as a new file** (Archicad, tested). Revit is expected to **Link IFC**; untested. Bonsai is an IFC working environment; **not tested** |
| Pipe reference | `RMInbound` → save by hand → attach Worksession by hand | BIM **IFC4** export, 3D pipes only. Real pipe export is untested. Inbound puts Z back on the Rhino model |
| Settings and docs | `RMOpen` | — |

BIM has no LoopFlow buttons.

## Terms

| Term | Meaning |
|---|---|
| **Storey frame** | A closed horizontal curve you draw, one per storey, at that storey’s height. It must sit **outside** the outer walls; touching the frame stops the publish. |
| **FL** | Structural-floor elevation. Do not enter FFL (finished floor). LoopFlow drawings use FFL; mixing them is about one finish thickness off. |
| **Whole / partial** | `RMStorey` WholeBuilding or PartialStoreys. If you only modelled a few floors, do not invent 1F or RF. |
| **IfcPlate / IfcCovering** | Unset types write as Plate. Ceilings should be Covering. Proxy objects are often invisible in Archicad. |
| **Worksession reference** | After attach, inbound meshes cannot be edited, but you can snap to them. Models skips reference objects so pipes are not sent back to BIM. |

## Where it stops

- Unsaved file: `RMModels` / `RMOpen` stop. `RMStorey` / `RMInbound` do not require a saved file.
- Missing frames, duplicate names or FL, or storey height not matching the frames: no publish.
- Geometry that touches a frame edge: stop. Same-layer objects outside the frame: skip. Below the lowest frame: skip (the command line lists the count).
- Cancel, fail, or interrupt: the last good `R2M.ifc` is not overwritten. The source Rhino file returns to its previous state.

## How to click

This page is the logic. Paste lines, frames, and Archicad open: [Commands](./COMMANDS.md).
