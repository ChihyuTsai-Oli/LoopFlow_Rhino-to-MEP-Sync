# LoopFlow｜Rhino to MEP Sync

[繁體中文](./README_zh-TW.md)

> **Development draft.** Command names, screen names, and install method are not frozen. There is no Package Manager package or toolbar yet. Do not treat this page as a published install guide.

Rhino publishes an architectural-shell IFC for Revit / Archicad / Blender Bonsai. Those tools publish MEP IFC back as **locked Worksession reference geometry** in Rhino. Design changes stay in Rhino. Exchange format is **IFC only**. There is no LoopFlow plug-in on the BIM side.

[▶ Documentation](./docs/README.md) · [▶ GitHub](https://github.com/ChihyuTsai-Oli/LoopFlow_Rhino-to-MEP-Sync)

## Features

- **Architectural shell** — Write selected layers to one shell IFC, hung on storey frames
- **Storey frames** — Draw a closed horizontal curve per storey; register names and FL (structural floor) elevations
- **MEP inbound** — Convert a BIM 3D-pipe IFC into locked meshes, then attach them by hand as a Worksession
- **Open / Health** — Config folder and last-good timestamps

No camera, lights, or live link. Do not use inbound geometry for drawings or as a Tag source.

## Requirements

- **Rhino 8** (Windows)
- **Archicad**, **Revit**, or **Blender Bonsai** (3D BIM is required)

Testing currently uses Archicad. Opening the IFC as a new file (File → Open) has passed for whole-building and partial-storey files. Revit and Bonsai are untested. Exporting a real pipe IFC is also untested.

Rhino dialogs are English. Traditional Chinese is the source of truth for this draft.

## How to run during development

A formal yak is not packed yet. Paste the ScriptEditor line from [Commands](./docs/COMMANDS.md) into the Rhino **command line**. Names (`RMOpen`, `RMStorey`, `RMModels`, `RMInbound`) are provisional and not registered as product commands.

Save the `.3dm` first (Inbound may use an unsaved blank file). The folder that holds the `.3dm` is the work folder. Settings and IFC live next to it in `_LoopFlow_Config/loopflow_R2M/`.

## Quick start

1. Draw storey frames and run `RMStorey`.
2. Run `RMModels` to write `models/R2M.ifc`.
3. Archicad: **File → Open** the IFC as a new file. Do not Merge.
4. Draw a few **3D** ducts or pipes that cross the ceiling, then export **IFC4** with the built-in exporter (3D pipes only).
5. In a blank Rhino file, run `RMInbound`, save by hand, then attach that `.3dm` as a Worksession in the working file.

See the [overview](./docs/USER_GUIDE.md) and [commands](./docs/COMMANDS.md) for the buttons and stops.

## License

MIT. See [LICENSE](./LICENSE).
