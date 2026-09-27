# LoopFlow｜Rhino to MEP Sync

[繁體中文](./README_zh-TW.md)

Rhino publishes an architectural-shell IFC for Revit, Archicad, and Blender Bonsai. BIM sends MEP geometry back as IFC, which Rhino attaches as a Worksession reference. **Design stays in Rhino.** Exchange is IFC only. There is no LoopFlow plug-in on the BIM side.

[▶ Documentation](./docs/README.md) · [▶ GitHub](https://github.com/ChihyuTsai-Oli/LoopFlow_Rhino-to-MEP-Sync)

Command names are frozen: `RMOpen`, `RMStorey`, `RMModels`, `RMInbound`. There is no Package Manager package yet. For now, open the development toolbar `wip/docs/toolbar/LoopFlow_R2M.rui` (buttons still run ScriptEditor). Dialogs are in English; Traditional Chinese is the source of truth for this guide.

## Features

- **Storey registration** — Draw a closed horizontal curve on each floor by hand, then register its name and FL (structural floor elevation)
- **Architectural shell** — Write the selected layers to one IFC, hung on those frames (length unit: centimetres)
- **Height correction** — Heights in BIM follow FL. `RMInbound` shifts inbound geometry back onto the Rhino model’s Z, so it does not sit at the building-elevation numbers
- **Pipe / wall reference** — BIM IFC becomes unlocked meshes. Save by hand, then attach as a Worksession to overlay against the model
- **Open / Health** — Config folder and last successful publish time

No camera, lights, or live link. Do not use inbound geometry for drawings or as a Tag source.

## Requirements

- **Rhino 8** (Windows)
- **Archicad**, **Revit**, or **Blender Bonsai** (3D BIM is required)

Exchange is **IFC only**. Archicad: File → Open as a new file (do not Merge). Revit: Link IFC, then create Levels at the frame elevations and open Floor Plans. Bonsai is listed as another IFC working environment; **this product does not test it**.

Receiving the shell and bringing walls back (including height correction) has passed in Archicad and Revit. Real ducts and pipes have not been tested.

## How to run for now

Open the development toolbar, or paste the ScriptEditor line from [Commands](./docs/COMMANDS.md) into the Rhino **command prompt**. Save the `.3dm` first (Inbound may use a blank new file). The folder that holds the `.3dm` is the work folder. Settings and IFC live next to it in `_LoopFlow_Config/loopflow_R2M/`.

A whole-building file and a partial-storey file in the same folder share one `config.json`. To inbound against the partial file, run `RMModels` on that file first so the correction value matches it.

## Quick start

1. Draw storey frames and run `RMStorey`.
2. Run `RMModels` to write `models/R2M.ifc`. If you need both a whole-building and a partial copy, rename immediately after publish.
3. Archicad: **File → Open** the IFC as a new file. Revit: **Link IFC**, then create matching Levels and Floor Plans.
4. Draw 3D geometry (walls are fine for a test), export **IFC4** with the built-in exporter, selected objects only, no extra coordinate offset.
5. In a blank Rhino file, run `RMInbound` (pick the working file’s `config.json`), save by hand, then attach that `.3dm` as a Worksession. Inbound height should match the Rhino model.

Step-by-step: [overview](./docs/USER_GUIDE.md) and [commands](./docs/COMMANDS.md).

## License and credits

MIT. See [LICENSE](./LICENSE). Icon credits: [CREDITS](./CREDITS.md).
