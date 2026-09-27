"""產生開發期 LoopFlow_R2M.rui（按鈕跑 ScriptEditor 入口）。

圖示為原創線稿，不是 Noun Project。正式 yak 之後把 <script> 改成 ! _RMOpen 等註冊指令。
重跑本檔會覆寫 rui；GUID 由名稱穩定產生，不要手改 rui 裡的 guid。
"""
from __future__ import annotations

import uuid
from pathlib import Path
from xml.sax.saxutils import escape

NS = uuid.UUID("7c2e1a90-4b6f-4d11-9e3a-0f8c2b5d7a11")
REPO_ROOT = Path(__file__).resolve().parents[2]
COMMANDS = REPO_ROOT / "wip" / "commands"
OUT = REPO_ROOT / "wip" / "docs" / "toolbar" / "LoopFlow_R2M.rui"
SCRIPT_ROOT = r"E:\_GitHub\LoopFlow_Rhino-to-MEP-Sync\wip\commands"


def gid(name: str) -> str:
    return str(uuid.uuid5(NS, name))


BUTTONS = (
    ("open", "Open", "Config folder and last publish", "RMOpen.py"),
    ("storey", "Storey", "Register storey frames and FL", "RMStorey.py"),
    ("models", "Models", "Publish architectural-shell IFC", "RMModels.py"),
    ("inbound", "Inbound", "Import BIM geometry with height correction", "RMInbound.py"),
)

ICONS = {
    "open": (
        '<rect x="6" y="18" width="36" height="22" rx="2"/>'
        '<path d="M6 18 V14 H18 L22 18 H42"/>'
    ),
    "storey": (
        '<rect x="8" y="8" width="32" height="10"/>'
        '<rect x="8" y="19" width="32" height="10"/>'
        '<rect x="8" y="30" width="32" height="10"/>'
    ),
    "models": (
        '<path d="M10 18 L24 8 L38 18 V40 H10 Z"/>'
        '<rect x="20" y="26" width="8" height="14"/>'
    ),
    "inbound": (
        '<path d="M24 6 V26"/>'
        '<path d="M16 18 L24 28 L32 18"/>'
        '<rect x="10" y="28" width="28" height="12"/>'
    ),
}


def svg(inner: str, stroke: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" version="1.1" '
        f'viewBox="0 0 48 48" fill="none" stroke="{stroke}" stroke-width="2" '
        f'stroke-linejoin="round" stroke-linecap="round">{inner}</svg>'
    )


def icon_xml(key: str) -> str:
    guid = gid(f"icon.{key}")
    inner = ICONS[key]
    return (
        f'    <icon guid="{guid}" name="{guid}.svg">\n'
        f"      <light>\n        {svg(inner, '#000000')}\n      </light>\n"
        f"      <dark>\n        {svg(inner, '#e5e5e5')}\n      </dark>\n"
        f"    </icon>"
    )


def macro_xml(key: str, title: str, help_text: str, script_file: str) -> str:
    guid = gid(f"macro.{key}")
    bitmap = gid(f"icon.{key}")
    path = f"{SCRIPT_ROOT}\\{script_file}"
    script = f'! _-ScriptEditor _Run "{path}"'
    loc = escape(title)
    help_ = escape(help_text)
    return f"""    <macro_item guid="{guid}" bitmap_id="{bitmap}">
      <tooltip>
        <locale_1033>{loc}</locale_1033>
      </tooltip>
      <help_text>
        <locale_1033>{help_}</locale_1033>
      </help_text>
      <button_text>
        <locale_1033>{loc}</locale_1033>
      </button_text>
      <menu_text>
        <locale_1033>{loc}</locale_1033>
      </menu_text>
      <script>{escape(script)}</script>
    </macro_item>"""


def main() -> int:
    ui = gid("ui")
    group = gid("group")
    bar = gid("bar")
    bar_bitmap = gid("icon.open")
    items = []
    spacer_n = 0
    order = ["open", "storey", "models", "inbound"]
    for i, key in enumerate(order):
        items.append(
            f'      <tool_bar_item guid="{gid(f"item.{key}")}">\n'
            f'        <left_macro_id>{gid(f"macro.{key}")}</left_macro_id>\n'
            f"      </tool_bar_item>"
        )
        if i in (0, 2):
            spacer_n += 1
            items.append(
                f'      <tool_bar_item guid="{gid(f"spacer.{spacer_n}")}" button_style="spacer" />'
            )

    macros = "\n".join(
        macro_xml(key, title, help_text, script)
        for key, title, help_text, script in BUTTONS
    )
    icons = "\n".join(icon_xml(key) for key, *_rest in BUTTONS)

    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<RhinoUI major_ver="5" minor_ver="0" guid="{ui}">
  <tool_bar_groups>
    <tool_bar_group guid="{group}" dock="top" visable="true" active_tool_bar="{bar}" hide_single_tab="False">
      <text>
        <locale_1033>LoopFlow R2M</locale_1033>
      </text>
      <tool_bar_group_item guid="{bar}" major_version="1" minor_version="1">
        <text>
          <locale_1033>LoopFlow R2M</locale_1033>
        </text>
        <tool_bar_id>{bar}</tool_bar_id>
      </tool_bar_group_item>
    </tool_bar_group>
  </tool_bar_groups>
  <tool_bars>
    <tool_bar guid="{bar}" bitmap_id="{bar_bitmap}">
      <text>
        <locale_1033>LoopFlow R2M</locale_1033>
      </text>
{chr(10).join(items)}
    </tool_bar>
  </tool_bars>
  <macros>
{macros}
  </macros>
  <icons>
{icons}
  </icons>
  <bitmaps>
    <small_bitmap item_width="0" item_height="0" />
    <normal_bitmap item_width="0" item_height="0" />
    <large_bitmap item_width="0" item_height="0" />
  </bitmaps>
</RhinoUI>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(xml, encoding="utf-8-sig", newline="\n")
    missing = [name for _k, _t, _h, name in BUTTONS if not (COMMANDS / name).is_file()]
    if missing:
        raise SystemExit("missing command scripts: " + ", ".join(missing))
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
