# LoopFlow R2M Commands

> **Development draft.** Command names are not frozen. There is no package or toolbar yet.
>
> Overview: [User guide](./USER_GUIDE.md). Names below are provisional (joined, e.g. `RMModels`) and are **not** registered Rhino product commands yet.
>
> Rhino dialogs are English.

## How to run during development

A formal yak is not installed. Paste one full line into the Rhino **command line** and press Enter. Both computers use `E:\_GitHub` as the Git root. Run on an isolated file; do not touch the live working document.

Each ScriptEditor run drops the already-loaded module, so re-running in the same Rhino window picks up new code from disk.

## Quick index

| Stage | Rhino | BIM | One line |
|---|---|---|---|
| Open | `RMOpen` | — | Config root, last-good time, folders or this guide |
| Storeys | `RMStorey` | — | Name frames and FL |
| Shell | `RMModels` | Open IFC as a new file | Selected layers → `R2M.ifc` |
| Pipes | `RMInbound` | Built-in IFC4 export | Locked meshes in a blank file; save and attach by hand |

## Contents

[01 Open and docs](#01-open-and-docs) · [02 Storey frames](#02-storey-frames) · [03 Architectural shell](#03-architectural-shell) · [04 BIM receive](#04-bim-receive) · [05 Pipe inbound](#05-pipe-inbound) · [06 Do not](#06-do-not)

---

## 01　Open and docs

**Command:** `RMOpen` (save first)

```
! _-ScriptEditor _Run "E:\_GitHub\LoopFlow_Rhino-to-MEP-Sync\wip\commands\RMOpen.py"
```

An English Health window lists the config root and last-good timestamps. An unsaved file is blocked.

Buttons:

- **Open Config** — `_LoopFlow_Config/loopflow_R2M/`
- **Open models** — folder that holds `R2M.ifc`
- **Open Docs** — currently the local `docs/` folder (entry: [docs/README.md](./README.md)). After this guide is on GitHub, the button will open that page.

---

## 02　Storey frames

**Command:** `RMStorey` (a saved file is not required; without one there is simply no log)

```
! _-ScriptEditor _Run "E:\_GitHub\LoopFlow_Rhino-to-MEP-Sync\wip\commands\RMStorey.py"
```

Models will not publish until **R2M storey frames** exist.

### Draw the frames

Draw a closed curve **per storey, at that storey’s own height**. Any closed horizontal planar curve is enough.

- **The frame must sit outside the outer walls.** Objects that touch the edge stop `RMModels`.
- Park temporary edits outside the frame (for example x+1000); they are skipped. You do not have to change layer.
- **RF is required in whole-building mode.** Roof slabs and parapets hang on RF. If you only modelled a few floors, do not invent RF — use partial mode.
- **Roof pops:** draw another frame above RF (plant rooms, tanks, stair bulkheads). They become R2F, R3F.
- **No roof pop:** draw nothing extra. The top storey has no upper bound; anything above it hangs there.
- Basements go below 1F and become B1, B2 (nearest first).

**Partial files and spanning objects:** if a bbox bottom or top sits outside the frames you already drew, draw that extra storey frame too, or Archicad will look incomplete. Bottom too low = skipped below the lowest storey. Top too high = the other file has no storey for it and geometry looks glued to the storey below. Whole-building mode already has the full stack. Do not invent empty storeys.

### Register

A note appears first: frames must be closed, horizontal, and strictly larger than the objects you will publish. Select all frames, then pick **WholeBuilding** or **PartialStoreys** in the dialog (do not press Enter on the command line to choose the mode).

**WholeBuilding**

1. Select every storey frame → Enter
2. Select the 1F frame → Enter
3. Enter the 1F elevation (document units; centimetres in a cm file) → Enter
4. Select the RF frame → Enter

Other elevations come from each frame’s Z. Names are B1 / 1F / 2F / RF / R2F in order.

**PartialStoreys**

Use this when the model is not the whole building (for example only 5F of 20). **Do not** invent 1F or RF, and **do not** insert empty IFC storeys.

1. Select the frames that actually exist → Enter
2. Pick one as the datum → Enter
3. Enter that storey’s name (e.g. `5F`) → Enter
4. Enter that storey’s FL (e.g. `1600`) → Enter

The rest are numbered by frame height (6F above 5F; B1 below 1F). Partial mode does not create RF / R2F.

Both modes move frames to layer `R2M::Storey` and write UserText `R2M_StoreyName` and `R2M_FL` (FL = structural floor).

### Edit

- **Change storey height:** move the frame, run `RMStorey` again.
- **Rename:** you may edit `R2M_StoreyName`, but **re-running `RMStorey` overwrites names** with the automatic sequence.
- **Do not hand-edit `R2M_FL`.** `RMStorey` writes it. FL may be a building elevation; it does not have to equal the frame’s model Z.
- Use **FL**, not FFL. LoopFlow drawings record FFL; they differ by one finish thickness (about 3–5 cm). The two products do not read each other — change both when the storey height changes.

---

## 03　Architectural shell

**Command:** `RMModels` (save first; `RMStorey` must already have run)

```
! _-ScriptEditor _Run "E:\_GitHub\LoopFlow_Rhino-to-MEP-Sync\wip\commands\RMModels.py"
```

One English dialog:

1. **Confirm storeys** — lists frames, FL, and frame Z. Missing frames, duplicate names or FL, or a height mismatch stops the run.
2. **Exclude token** (default `//`; blank = none). Layer paths that contain it are skipped.
3. **Leaf layers only.** **Select All** / **Select None**. First run: nothing checked. Whole-building and partial files in the same folder remember their own checks.
4. **IFC type** — checked layers export. Default dropdown is `IfcPlate`. Ceilings: `IfcCovering`. Walls / slabs / columns / beams / stairs should be changed to the matching type. A stored Proxy shows as Plate. Uncheck to hide.
5. **Geometry kinds** — counts shown; Point / Curve off by default.
6. **Mesh density** — coarse / medium / fine; default medium.

Buttons:

- **Save Config** — write this file’s panel now; dialog stays open
- **Load Config** — restore this file’s last saved panel
- **Publish** — write the panel, then the IFC
- **Cancel**

Success writes `models/R2M.ifc`. Failure does not overwrite last good. The source Rhino file returns to its previous state.

On publish:

- Only objects **strictly inside** that storey’s frame export; touching the edge stops; same-layer objects outside skip; below the lowest storey skip.
- Worksession references are not packed into the shell IFC.
- If more than half the objects are still Proxy, the command line warns that Archicad may hide them.
- The product filename is always `R2M.ifc`. Keep your own renamed copies if you need both a whole-building and a partial file.

---

## 04　BIM receive

There is no LoopFlow on the BIM side. The shell is a **reference**, not a model for the other office to take over.

**Archicad (tested)**

1. **File → Open** the `R2M.ifc` as a new file.
2. You do not need to delete default Stories.
3. **Do not Merge.** Merging a partial file can map IFC storey 0 onto Ground Floor.
4. Do not Update into an existing template (Ground Floor then cannot be deleted).

For a partial file, include every extra frame that spanning objects reach, then publish again.

**Revit (untested)**

Expected: **Link IFC**, not Open or Import, so Rhino can overwrite the same `R2M.ifc` and the link can reload. Do not treat this as verified until it has been tested.

Ceilings should be `IfcCovering` in Rhino. Unchanged dropdowns write `IfcPlate`. Proxy objects are often invisible in Archicad.

---

## 05　Pipe inbound

**Command:** `RMInbound` (a blank file is enough; a saved file is not required)

```
! _-ScriptEditor _Run "E:\_GitHub\LoopFlow_Rhino-to-MEP-Sync\wip\commands\RMInbound.py"
```

BIM should export **3D pipes only** (clash segments or checked systems; not the whole building, not 2D). Insulation / outer envelope is useful. No specific library parts — a few 3D ducts or pipes that cross the ceiling are enough.

**Drawing pipes in Archicad (real export untested; menu labels not recorded)**

1. Open the shell IFC **as a new file** (a 2F / 3F / 4F file is easier against the ceiling).
2. Draw a few **3D** ducts or pipes that cross the ceiling height.
3. Use Archicad’s **built-in** IFC export: **IFC4**; 3D pipes only; no whole building, no 2D, no extra coordinate offset. Keep storeys as they are.
4. Name the file with the source (Archicad) and the date.

**Rhino**

1. Open a **blank `.3dm`** with the same units as the working file.
2. Paste the `RMInbound` line above and pick the IFC. Confirm the document units, then locked meshes are built. Object names are `IfcType:GlobalId`, split by IFC type on layers.
3. **Save** the `.3dm` yourself (suggested: `_LoopFlow_Config/loopflow_R2M/inbound/` next to the working file; keep a stable name).
4. Back in the working file, **attach** that `.3dm` as a Worksession yourself.

The command does **not** write, save, or attach. Reference objects cannot be edited; you can snap to them.

To update pipes: repeat Rhino steps 1–3 over the same `.3dm`, then Refresh in the Worksession manager. A stable filename is what makes that work.

Version 1 has **no** clash check and does not draw BIM clash points in Rhino. Look at inbound meshes overlapping the ceiling.

---

## 06　Do not

- Do not type `RMOpen` and the others as registered commands; paste the ScriptEditor line.
- Do not use inbound geometry for drawings or as a Tag source.
- Do not hand-edit `R2M_FL`.
- Do not insert a 0 m empty IFC storey to please Merge or a template.
- Do not convert the shell to native BIM elements and edit it there; design changes go back to Rhino.
- Do not send a whole-building or 2D IFC back as the pipe file.
