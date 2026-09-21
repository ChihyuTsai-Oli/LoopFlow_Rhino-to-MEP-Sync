"""RMModels 英文對話框；Eto 失敗時改走指令列。"""

from __future__ import annotations

from loopflow_r2m.exceptions import R2MStop
from loopflow_r2m.names import (
    DEFAULT_EXCLUDE_TOKEN,
    DEFAULT_MESH_DENSITY,
    GEOM_CLASSES,
    IFC_PRODUCT_TYPES,
    MESH_DENSITIES,
)


def _placeholder():
    return "(select type)"


def _normalize_exclude(text):
    if text is None:
        return ""
    return str(text).strip()


def show_models_dialog(storey_lines, layers, saved):
    """回傳選擇 dict；取消回 None。"""
    try:
        return _show_eto(storey_lines, layers, saved)
    except ImportError:
        return _show_cli(storey_lines, layers, saved)


def _collect_choice(exclude_text, layer_checks, geom, density):
    selected = []
    types = {}
    for path, checked, choice in layer_checks:
        if not checked:
            continue
        selected.append(path)
        if not choice or choice == _placeholder():
            raise R2MStop("Select an IFC type for layer: %s" % path)
        if choice not in IFC_PRODUCT_TYPES:
            raise R2MStop("Unknown IFC type for layer: %s" % path)
        types[path] = str(choice)
    if not selected:
        raise R2MStop("No layers selected.")
    if density not in MESH_DENSITIES:
        density = DEFAULT_MESH_DENSITY
    return {
        "exclude_token": _normalize_exclude(exclude_text),
        "layer_paths": selected,
        "layer_type_map": types,
        "geom": geom,
        "mesh_density": str(density),
    }


def _show_eto(storey_lines, layers, saved):
    import Eto.Drawing as ed
    import Eto.Forms as ef
    from Rhino.UI import RhinoEtoApp

    saved = saved or {}
    saved_types = dict(saved.get("layer_type_map") or {})
    saved_layers = list(saved.get("layer_paths") or [])
    saved_geom = saved.get("geom") or {}
    exclude0 = saved.get("exclude_token", DEFAULT_EXCLUDE_TOKEN)
    density0 = saved.get("mesh_density", DEFAULT_MESH_DENSITY)
    if density0 not in MESH_DENSITIES:
        density0 = DEFAULT_MESH_DENSITY

    dlg = ef.Dialog[bool]()
    dlg.Title = "RMModels"
    dlg.Padding = ed.Padding(12)
    dlg.ClientSize = ed.Size(720, 760)

    storey_box = ef.TextArea()
    storey_box.ReadOnly = True
    storey_box.Text = "\n".join(storey_lines)
    storey_box.Height = 80

    exclude_box = ef.TextBox()
    exclude_box.Text = "" if exclude0 is None else str(exclude0)

    type_choices = [_placeholder()] + list(IFC_PRODUCT_TYPES)
    layer_widgets = []
    layer_stack = ef.DynamicLayout()
    layer_stack.Spacing = ed.Size(4, 4)
    for row in layers:
        path = row["path"]
        check = ef.CheckBox()
        check.Text = "%s  (%s)" % (path, row["count"])
        check.Checked = path in saved_layers if saved_layers else row["count"] > 0
        drop = ef.DropDown()
        drop.DataStore = type_choices
        previous = saved_types.get(path)
        drop.SelectedIndex = type_choices.index(previous) if previous in type_choices else 0
        line = ef.DynamicLayout()
        line.DefaultSpacing = ed.Size(8, 0)
        line.AddRow(check, drop)
        layer_stack.AddRow(line)
        layer_widgets.append((path, check, drop))

    layer_scroll = ef.Scrollable()
    layer_scroll.Content = layer_stack
    layer_scroll.Height = 280

    geom_checks = {}
    geom_stack = ef.DynamicLayout()
    geom_stack.Spacing = ed.Size(8, 4)
    row_items = []
    for key, label, default in GEOM_CLASSES:
        box = ef.CheckBox()
        box.Text = label
        box.Checked = bool(saved_geom.get(key, default))
        geom_checks[key] = box
        row_items.append(box)
        if len(row_items) == 4:
            geom_stack.AddRow(*row_items)
            row_items = []
    if row_items:
        geom_stack.AddRow(*row_items)

    density_choices = list(MESH_DENSITIES)
    density_list = ef.RadioButtonList()
    density_list.Orientation = ef.Orientation.Horizontal
    density_list.DataStore = density_choices
    density_list.SelectedIndex = density_choices.index(density0)

    ok = ef.Button(Text="Publish")
    cancel = ef.Button(Text="Cancel")

    def on_ok(sender, args):
        dlg.Close(True)

    def on_cancel(sender, args):
        dlg.Close(False)

    ok.Click += on_ok
    cancel.Click += on_cancel
    dlg.DefaultButton = ok
    dlg.AbortButton = cancel

    buttons = ef.DynamicLayout()
    buttons.AddRow(None, cancel, ok)

    root = ef.DynamicLayout()
    root.Spacing = ed.Size(8, 8)
    root.AddRow(ef.Label(Text="Storeys (FL)"))
    root.AddRow(storey_box)
    root.AddRow(ef.Label(Text="Exclude token (blank = none)"))
    root.AddRow(exclude_box)
    root.AddRow(ef.Label(Text="Layers — check to export; pick IFC type per layer"))
    root.AddRow(layer_scroll)
    root.AddRow(ef.Label(Text="Geometry types"))
    root.AddRow(geom_stack)
    root.AddRow(ef.Label(Text="Mesh density"))
    root.AddRow(density_list)
    root.AddRow(buttons)
    dlg.Content = root

    owner = RhinoEtoApp.MainWindow
    result = dlg.ShowModal(owner) if owner is not None else dlg.ShowModal()
    if not result:
        return None

    layer_checks = []
    for path, check, drop in layer_widgets:
        index = int(drop.SelectedIndex)
        choice = type_choices[index] if 0 <= index < len(type_choices) else None
        layer_checks.append((path, bool(check.Checked), choice))
    geom = {key: bool(box.Checked) for key, box in geom_checks.items()}
    density_index = int(density_list.SelectedIndex)
    density = (
        density_choices[density_index]
        if 0 <= density_index < len(density_choices)
        else DEFAULT_MESH_DENSITY
    )
    return _collect_choice(exclude_box.Text, layer_checks, geom, density)


def _ask_string(prompt, default=""):
    import Rhino

    getter = Rhino.Input.Custom.GetString()
    getter.SetCommandPrompt(prompt)
    if default not in (None, ""):
        getter.SetDefaultString(str(default))
    result = getter.Get()
    if result == Rhino.Input.GetResult.Cancel:
        return None
    if result == Rhino.Input.GetResult.String:
        return getter.StringResult()
    return default


def _show_cli(storey_lines, layers, saved):
    saved = saved or {}
    print("Storeys:")
    for line in storey_lines:
        print("  " + line)

    exclude = _ask_string(
        "Exclude token (blank = none)",
        saved.get("exclude_token", DEFAULT_EXCLUDE_TOKEN) or "",
    )
    if exclude is None:
        return None

    print("Layers:")
    for index, row in enumerate(layers, start=1):
        print("  %s. %s (%s)" % (index, row["path"], row["count"]))
    saved_layers = list(saved.get("layer_paths") or [])
    default_idx = []
    for index, row in enumerate(layers, start=1):
        if saved_layers:
            if row["path"] in saved_layers:
                default_idx.append(str(index))
        elif row["count"] > 0:
            default_idx.append(str(index))
    picked = _ask_string("Layer numbers (comma-separated)", ",".join(default_idx))
    if picked is None:
        return None
    selected_index = set()
    for part in str(picked).replace(" ", "").split(","):
        if not part:
            continue
        try:
            selected_index.add(int(part))
        except ValueError:
            raise R2MStop("Layer numbers must be integers.")

    saved_types = dict(saved.get("layer_type_map") or {})
    layer_checks = []
    for index, row in enumerate(layers, start=1):
        if index not in selected_index:
            layer_checks.append((row["path"], False, None))
            continue
        default_type = saved_types.get(row["path"], "")
        choice = _ask_string(
            "IFC type for %s (%s)" % (row["path"], ", ".join(IFC_PRODUCT_TYPES)),
            default_type,
        )
        if choice is None:
            return None
        layer_checks.append((row["path"], True, str(choice).strip()))

    saved_geom = saved.get("geom") or {}
    geom = {}
    for key, label, default in GEOM_CLASSES:
        current = saved_geom.get(key, default)
        answer = _ask_string("Include %s? Yes/No" % label, "Yes" if current else "No")
        if answer is None:
            return None
        geom[key] = str(answer).strip().lower() in ("y", "yes", "1", "true")

    density = _ask_string(
        "Mesh density (coarse/medium/fine)",
        saved.get("mesh_density", DEFAULT_MESH_DENSITY),
    )
    if density is None:
        return None
    return _collect_choice(exclude, layer_checks, geom, str(density).strip().lower())


def confirm_yes(prompt, title="R2M"):
    """是／否。取消或否回 False。"""
    try:
        from Eto.Forms import MessageBox, MessageBoxButtons, DialogResult

        result = MessageBox.Show(prompt, title, MessageBoxButtons.YesNo)
        return result == DialogResult.Yes
    except Exception:
        import Rhino

        getter = Rhino.Input.Custom.GetOption()
        getter.SetCommandPrompt(prompt + " (Yes/No)")
        getter.AddOption("Yes")
        getter.AddOption("No")
        result = getter.Get()
        if result != Rhino.Input.GetResult.Option:
            return False
        name = getter.Option().EnglishName
        return name == "Yes"


def pick_ifc_file():
    """回傳路徑字串，取消則 None。"""
    import Rhino.UI

    dialog = Rhino.UI.OpenFileDialog()
    dialog.Filter = "IFC files (*.ifc)|*.ifc"
    dialog.Title = "RMInbound"
    if not dialog.ShowOpenDialog():
        return None
    return dialog.FileName


def show_open_health(lines, folders):
    """顯示 Health；按鈕打開資料夾。取消回 False。"""
    try:
        return _show_open_eto(lines, folders)
    except ImportError:
        return _show_open_cli(lines, folders)


def _open_path(path):
    import os

    os.startfile(str(path))


def _show_open_eto(lines, folders):
    import Eto.Drawing as ed
    import Eto.Forms as ef
    from Rhino.UI import RhinoEtoApp

    dlg = ef.Dialog[bool]()
    dlg.Title = "RMOpen"
    dlg.Padding = ed.Padding(12)
    dlg.ClientSize = ed.Size(520, 360)

    box = ef.TextArea()
    box.ReadOnly = True
    box.Text = "\n".join(lines)
    box.Height = 180

    def make_open(folder):
        def handler(sender, args):
            if folder and __import__("pathlib").Path(folder).exists():
                _open_path(folder)

        return handler

    btn_config = ef.Button(Text="Open Config")
    btn_models = ef.Button(Text="Open Models")
    btn_docs = ef.Button(Text="Open Docs")
    btn_config.Click += make_open(folders.get("config"))
    btn_models.Click += make_open(folders.get("models"))
    btn_docs.Click += make_open(folders.get("docs"))
    close = ef.Button(Text="Close")

    def on_close(sender, args):
        dlg.Close(True)

    close.Click += on_close
    dlg.DefaultButton = close
    dlg.AbortButton = close

    buttons = ef.DynamicLayout()
    buttons.AddRow(btn_config, btn_models, btn_docs, None, close)

    root = ef.DynamicLayout()
    root.Spacing = ed.Size(8, 8)
    root.AddRow(box)
    root.AddRow(buttons)
    dlg.Content = root
    owner = RhinoEtoApp.MainWindow
    result = dlg.ShowModal(owner) if owner is not None else dlg.ShowModal()
    return bool(result)


def _show_open_cli(lines, folders):
    print("RMOpen:")
    for line in lines:
        print("  " + line)
    choice = _ask_string("Open Config / Models / Docs / Close", "Close")
    if choice is None:
        return False
    key = str(choice).strip().lower()
    mapping = {
        "config": folders.get("config"),
        "models": folders.get("models"),
        "docs": folders.get("docs"),
    }
    if key in mapping and mapping[key]:
        _open_path(mapping[key])
    return True

