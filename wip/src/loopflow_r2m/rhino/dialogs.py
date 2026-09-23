"""RMModels 英文對話框；Eto 失敗時改走指令列。"""

from __future__ import annotations

from loopflow_r2m.exceptions import R2MStop
from loopflow_r2m.names import (
    DEFAULT_EXCLUDE_TOKEN,
    DEFAULT_IFC_TYPE,
    DEFAULT_MESH_DENSITY,
    GEOM_CLASSES,
    IFC_PRODUCT_TYPES,
    LEGACY_DEFAULT_IFC_TYPE,
    MESH_DENSITIES,
    ifc_type_choices,
)


def _placeholder():
    return "(reference)"


def _is_unset_type(choice):
    """空白、舊佔位、舊預設 Proxy 都當成未選（開面板時改顯示 Plate）。"""
    text = "" if choice is None else str(choice).strip()
    return (not text) or text == _placeholder() or text == LEGACY_DEFAULT_IFC_TYPE


def _resolve_layer_type(choice):
    """未選或舊佔位視為 IfcPlate。下拉明示的 Proxy 仍寫 Proxy。"""
    text = "" if choice is None else str(choice).strip()
    if not text or text == _placeholder():
        return DEFAULT_IFC_TYPE
    if text not in IFC_PRODUCT_TYPES:
        raise R2MStop("Unknown IFC type for layer: %s" % text)
    return text


def _type_index(type_choices, previous):
    effective = DEFAULT_IFC_TYPE if _is_unset_type(previous) else previous
    if effective in type_choices:
        return type_choices.index(effective)
    return type_choices.index(DEFAULT_IFC_TYPE)


def _normalize_exclude(text):
    if text is None:
        return ""
    return str(text).strip()


def _eto_button(ef, text):
    """Rhino pythonnet 不接受 Button(Text=...)。"""
    btn = ef.Button()
    btn.Text = text
    return btn


def _eto_button_bar(ef, ed, *items):
    """按鈕列高度跟文字走，對齊 RMStorey。"""
    row = ef.DynamicLayout()
    row.Spacing = ed.Size(8, 0)
    row.AddRow(*items)
    return row


def _eto_add(layout, control, xscale, yscale):
    """DynamicLayout.Add(control, xscale, yscale)。舊 Eto 沒有第三參數時退回 AddRow。"""
    try:
        layout.Add(control, xscale, yscale)
    except TypeError:
        layout.AddRow(control)


def _eto_label(ef, text):
    """Rhino pythonnet 不接受 Label(Text=...)。"""
    label = ef.Label()
    label.Text = text
    return label


def _checkbox_on(box):
    """Eto CheckBox.Checked 在 pythonnet 是 bool，不是物件。"""
    return box.Checked is True


def show_models_dialog(storey_lines, layers, saved, on_save=None, on_load=None):
    """回傳選擇 dict；取消回 None。Save／Load 不關對話框。"""
    try:
        return _show_eto(storey_lines, layers, saved, on_save, on_load)
    except ImportError:
        return _show_cli(storey_lines, layers, saved)


def _snapshot_choice(exclude_text, layer_checks, geom, density):
    """可含零個勾選；未勾圖層的下拉類型也一併記住。"""
    selected = []
    types = {}
    for path, checked, choice in layer_checks:
        types[path] = _resolve_layer_type(choice)
        if checked:
            selected.append(path)
    if density not in MESH_DENSITIES:
        density = DEFAULT_MESH_DENSITY
    return {
        "exclude_token": _normalize_exclude(exclude_text),
        "layer_paths": selected,
        "layer_type_map": types,
        "geom": geom,
        "mesh_density": str(density),
    }


def _collect_choice(exclude_text, layer_checks, geom, density):
    result = _snapshot_choice(exclude_text, layer_checks, geom, density)
    if not result["layer_paths"]:
        raise R2MStop("No layers selected.")
    result["layer_type_map"] = {
        path: result["layer_type_map"][path] for path in result["layer_paths"]
    }
    return result


def _read_layer_checks(layer_widgets, type_choices):
    layer_checks = []
    for path, check, drop in layer_widgets:
        index = int(drop.SelectedIndex)
        choice = type_choices[index] if 0 <= index < len(type_choices) else None
        layer_checks.append((path, _checkbox_on(check), choice))
    return layer_checks


def _apply_panel(
    saved,
    exclude_box,
    layer_widgets,
    type_choices,
    geom_checks,
    density_list,
    density_choices,
):
    saved = saved or {}
    exclude_box.Text = "" if saved.get("exclude_token") is None else str(saved.get("exclude_token"))
    saved_types = dict(saved.get("layer_type_map") or {})
    saved_layers = list(saved.get("layer_paths") or [])
    for path, check, drop in layer_widgets:
        check.Checked = path in saved_layers
        drop.SelectedIndex = _type_index(type_choices, saved_types.get(path))
    saved_geom = saved.get("geom") or {}
    for key, _label, default in GEOM_CLASSES:
        if key in geom_checks:
            geom_checks[key].Checked = bool(saved_geom.get(key, default))
    density0 = saved.get("mesh_density", DEFAULT_MESH_DENSITY)
    if density0 not in MESH_DENSITIES:
        density0 = DEFAULT_MESH_DENSITY
    density_list.SelectedIndex = density_choices.index(density0)


def _show_eto(storey_lines, layers, saved, on_save=None, on_load=None):
    import Eto.Drawing as ed
    import Eto.Forms as ef
    from Rhino.UI import RhinoEtoApp

    saved = saved or {}

    dlg = ef.Dialog[bool]()
    dlg.Title = "RMModels"
    dlg.Padding = ed.Padding(12)
    dlg.ClientSize = ed.Size(720, 760)

    storey_box = ef.TextArea()
    storey_box.ReadOnly = True
    storey_box.Text = "\n".join(storey_lines)
    storey_box.Height = 110

    exclude_box = ef.TextBox()

    type_choices = list(ifc_type_choices())
    layer_widgets = []
    layer_stack = ef.DynamicLayout()
    layer_stack.Spacing = ed.Size(4, 4)
    for row in layers:
        path = row["path"]
        check = ef.CheckBox()
        check.Text = "%s  (%s)" % (path, row["count"])
        drop = ef.DropDown()
        drop.DataStore = type_choices
        line = ef.DynamicLayout()
        line.DefaultSpacing = ed.Size(8, 0)
        line.AddRow(check, drop)
        layer_stack.AddRow(line)
        layer_widgets.append((path, check, drop))

    layer_scroll = ef.Scrollable()
    layer_scroll.Content = layer_stack
    layer_scroll.Height = 280

    def on_select_all(sender, args):
        for _path, check, _drop in layer_widgets:
            check.Checked = True

    def on_select_none(sender, args):
        for _path, check, _drop in layer_widgets:
            check.Checked = False

    select_all = _eto_button(ef, "Select All")
    select_none = _eto_button(ef, "Select None")
    select_all.Click += on_select_all
    select_none.Click += on_select_none
    layer_toolbar = ef.DynamicLayout()
    layer_toolbar.Spacing = ed.Size(8, 0)
    layer_toolbar.AddRow(select_all, select_none, None)

    geom_checks = {}
    geom_stack = ef.DynamicLayout()
    geom_stack.Spacing = ed.Size(8, 4)
    row_items = []
    for key, label, default in GEOM_CLASSES:
        box = ef.CheckBox()
        box.Text = label
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

    _apply_panel(
        saved,
        exclude_box,
        layer_widgets,
        type_choices,
        geom_checks,
        density_list,
        density_choices,
    )

    ok = _eto_button(ef, "Publish")
    cancel = _eto_button(ef, "Cancel")
    save_btn = _eto_button(ef, "Save Config")
    load_btn = _eto_button(ef, "Load Config")

    def _current_snapshot():
        layer_checks = _read_layer_checks(layer_widgets, type_choices)
        geom = {key: _checkbox_on(box) for key, box in geom_checks.items()}
        density_index = int(density_list.SelectedIndex)
        density = (
            density_choices[density_index]
            if 0 <= density_index < len(density_choices)
            else DEFAULT_MESH_DENSITY
        )
        return _snapshot_choice(exclude_box.Text, layer_checks, geom, density)

    def on_ok(sender, args):
        if not any(_checkbox_on(check) for _path, check, _drop in layer_widgets):
            from Eto.Forms import MessageBox

            MessageBox.Show("Check at least one layer.", dlg.Title)
            return
        dlg.Close(True)

    def on_cancel(sender, args):
        dlg.Close(False)

    def on_save_click(sender, args):
        from Eto.Forms import MessageBox

        if on_save is None:
            MessageBox.Show("Save Config is not available.", dlg.Title)
            return
        try:
            on_save(_current_snapshot())
        except Exception as exc:
            MessageBox.Show(str(exc), dlg.Title)
            return
        MessageBox.Show("Saved.", dlg.Title)

    def on_load_click(sender, args):
        from Eto.Forms import MessageBox

        if on_load is None:
            MessageBox.Show("No saved panel for this file.", dlg.Title)
            return
        loaded = on_load()
        if not loaded:
            MessageBox.Show("No saved panel for this file.", dlg.Title)
            return
        _apply_panel(
            loaded,
            exclude_box,
            layer_widgets,
            type_choices,
            geom_checks,
            density_list,
            density_choices,
        )

    ok.Click += on_ok
    cancel.Click += on_cancel
    save_btn.Click += on_save_click
    load_btn.Click += on_load_click
    dlg.DefaultButton = ok
    dlg.AbortButton = cancel

    buttons = _eto_button_bar(ef, ed, None, save_btn, load_btn, cancel, ok)

    root = ef.DynamicLayout()
    root.Spacing = ed.Size(8, 8)
    root.AddRow(_eto_label(ef, "Storeys (FL)"))
    root.AddRow(storey_box)
    root.AddRow(_eto_label(ef, "Exclude token (blank = none)"))
    root.AddRow(exclude_box)
    root.AddRow(_eto_label(ef, "Layers — check at least one to export; type defaults to IfcPlate (ceilings: IfcCovering)"))
    root.AddRow(layer_toolbar)
    _eto_add(root, layer_scroll, True, True)
    root.AddRow(_eto_label(ef, "Geometry types"))
    root.AddRow(geom_stack)
    root.AddRow(_eto_label(ef, "Mesh density"))
    root.AddRow(density_list)
    _eto_add(root, buttons, True, False)
    dlg.Content = root

    owner = RhinoEtoApp.MainWindow
    result = dlg.ShowModal(owner) if owner is not None else dlg.ShowModal()
    if not result:
        return None
    return _current_snapshot()


def ask_string(prompt, default=""):
    """指令列輸入字串。取消回 None。"""
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

    exclude = ask_string(
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
        if row["path"] in saved_layers:
            default_idx.append(str(index))
    picked = ask_string(
        "Layer numbers (comma-separated, All, or None)",
        ",".join(default_idx),
    )
    if picked is None:
        return None
    picked_text = str(picked).strip().lower()
    selected_index = set()
    if picked_text == "all":
        selected_index = set(range(1, len(layers) + 1))
    elif picked_text not in ("", "none"):
        for part in str(picked).replace(" ", "").split(","):
            if not part:
                continue
            try:
                selected_index.add(int(part))
            except ValueError:
                raise R2MStop("Layer numbers must be integers, All, or None.")

    saved_types = dict(saved.get("layer_type_map") or {})
    layer_checks = []
    for index, row in enumerate(layers, start=1):
        if index not in selected_index:
            layer_checks.append((row["path"], False, None))
            continue
        default_type = saved_types.get(row["path"], DEFAULT_IFC_TYPE)
        if _is_unset_type(default_type):
            default_type = DEFAULT_IFC_TYPE
        choice = ask_string(
            "IFC type for %s (blank = %s; ceilings = IfcCovering; %s)"
            % (row["path"], DEFAULT_IFC_TYPE, ", ".join(IFC_PRODUCT_TYPES)),
            default_type,
        )
        if choice is None:
            return None
        layer_checks.append((row["path"], True, str(choice).strip()))

    saved_geom = saved.get("geom") or {}
    geom = {}
    for key, label, default in GEOM_CLASSES:
        current = saved_geom.get(key, default)
        answer = ask_string("Include %s? Yes/No" % label, "Yes" if current else "No")
        if answer is None:
            return None
        geom[key] = str(answer).strip().lower() in ("y", "yes", "1", "true")

    density = ask_string(
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


def pick_curves(prompt, multiple):
    """選曲線。回傳 Guid tuple；取消或空選回 None。"""
    import Rhino

    getter = Rhino.Input.Custom.GetObject()
    getter.SetCommandPrompt(prompt)
    getter.GeometryFilter = Rhino.DocObjects.ObjectType.Curve
    getter.EnablePreSelect(multiple, True)
    getter.SubObjectSelect = False
    if multiple:
        result = getter.GetMultiple(1, 0)
    else:
        result = getter.Get()
    if result != Rhino.Input.GetResult.Object:
        return None
    ids = tuple(getter.Object(i).ObjectId for i in range(getter.ObjectCount))
    return ids or None


def ask_number(prompt, title="R2M"):
    """彈窗輸入數字。取消回 None；非數字則 R2MStop。"""
    text = _prompt_text(prompt, title)
    if text is None:
        return None
    try:
        return float(str(text).strip().replace(",", "."))
    except ValueError:
        raise R2MStop("%s is not a number: %s" % (prompt, text))


def ask_text(prompt, title="R2M"):
    """彈窗輸入字串。取消回 None。"""
    text = _prompt_text(prompt, title)
    if text is None:
        return None
    return str(text).strip()


def pick_option(prompt, names, title="R2M"):
    """選一個英文選項。取消回 None。

    優先彈窗。指令列 GetOption 在 ScriptEditor 裡按 Enter 會被當成取消，
    選完框後一按 Enter 指令就停。
    """
    names = tuple(names)
    try:
        return _pick_option_eto(prompt, names, title)
    except Exception:
        return _pick_option_cli(prompt, names)


def _pick_option_eto(prompt, names, title):
    import Eto.Drawing as ed
    import Eto.Forms as ef
    from Rhino.UI import RhinoEtoApp

    chosen = []
    dlg = ef.Dialog[bool]()
    dlg.Title = title
    dlg.Padding = ed.Padding(12)

    buttons = []

    def make(name):
        def handler(sender, args):
            chosen.append(name)
            dlg.Close(True)

        return handler

    for name in names:
        btn = _eto_button(ef, name)
        btn.Click += make(name)
        buttons.append(btn)

    cancel = _eto_button(ef, "Cancel")

    def on_cancel(sender, args):
        dlg.Close(False)

    cancel.Click += on_cancel
    dlg.AbortButton = cancel
    if buttons:
        dlg.DefaultButton = buttons[0]

    row = _eto_button_bar(ef, ed, *(buttons + [None, cancel]))

    root = ef.DynamicLayout()
    root.Spacing = ed.Size(8, 8)
    root.AddRow(_eto_label(ef, prompt))
    _eto_add(root, row, True, False)
    dlg.Content = root

    owner = RhinoEtoApp.MainWindow
    result = dlg.ShowModal(owner) if owner is not None else dlg.ShowModal()
    if not result or not chosen:
        return None
    return chosen[0]


def _pick_option_cli(prompt, names):
    import Rhino

    getter = Rhino.Input.Custom.GetOption()
    getter.SetCommandPrompt(prompt + " (click an option)")
    for name in names:
        getter.AddOption(name)
    result = getter.Get()
    if result != Rhino.Input.GetResult.Option:
        return None
    return getter.Option().EnglishName


def _prompt_text(prompt, title):
    """優先用彈窗；環境不支援時退回指令列。"""
    try:
        import Rhino.UI

        ok, value = Rhino.UI.Dialogs.ShowEditBox(title, prompt, "", False)
    except Exception:
        return ask_string(prompt)
    return value if ok else None


def pick_ifc_file():
    """回傳路徑字串，取消則 None。"""
    import Rhino.UI

    dialog = Rhino.UI.OpenFileDialog()
    dialog.Filter = "IFC files (*.ifc)|*.ifc"
    dialog.Title = "RMInbound"
    if not dialog.ShowOpenDialog():
        return None
    return dialog.FileName


def pick_config_file():
    """回傳 config.json 路徑，取消則 None。"""
    import Rhino.UI

    dialog = Rhino.UI.OpenFileDialog()
    dialog.Filter = "R2M config (config.json)|config.json|JSON files (*.json)|*.json"
    dialog.Title = "Pick working-file config.json (elevation shift)"
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

    btn_config = _eto_button(ef, "Open Config")
    btn_models = _eto_button(ef, "Open Models")
    btn_docs = _eto_button(ef, "Open Docs")
    btn_config.Click += make_open(folders.get("config"))
    btn_models.Click += make_open(folders.get("models"))
    btn_docs.Click += make_open(folders.get("docs"))
    close = _eto_button(ef, "Close")

    def on_close(sender, args):
        dlg.Close(True)

    close.Click += on_close
    dlg.DefaultButton = close
    dlg.AbortButton = close

    buttons = _eto_button_bar(ef, ed, btn_config, btn_models, btn_docs, None, close)

    root = ef.DynamicLayout()
    root.Spacing = ed.Size(8, 8)
    _eto_add(root, box, True, True)
    _eto_add(root, buttons, True, False)
    dlg.Content = root
    owner = RhinoEtoApp.MainWindow
    result = dlg.ShowModal(owner) if owner is not None else dlg.ShowModal()
    return bool(result)


def _show_open_cli(lines, folders):
    print("RMOpen:")
    for line in lines:
        print("  " + line)
    choice = ask_string("Open Config / Models / Docs / Close", "Close")
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

