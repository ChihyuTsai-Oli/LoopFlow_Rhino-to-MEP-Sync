"""產生開發期 LoopFlow_R2M.rui（按鈕跑已登錄的 `RMOpen` 等指令）。

圖示從同資料夾的五個 SVG 寫入：`LoopFlow_R2M.svg` 是工具列分頁圖，其餘四個是按鈕。
成功寫出 rui 後會刪掉這五個 SVG。重跑前再放回。GUID 由名稱穩定產生。
"""
from __future__ import annotations

import re
import uuid
from pathlib import Path
from xml.sax.saxutils import escape

NS = uuid.UUID("7c2e1a90-4b6f-4d11-9e3a-0f8c2b5d7a11")
REPO_ROOT = Path(__file__).resolve().parents[2]
COMMANDS = REPO_ROOT / "wip" / "commands"
TOOLBAR = REPO_ROOT / "wip" / "docs" / "toolbar"
OUT = TOOLBAR / "LoopFlow_R2M.rui"

BUTTONS = (
    ("open", "Open", "Config folder and last publish", "RMOpen", "R2M_Open.svg"),
    ("storey", "Storey", "Register storey frames and FL", "RMStorey", "R2M_Storey.svg"),
    ("models", "Models", "Publish architectural-shell IFC", "RMModels", "R2M_Models.svg"),
    ("inbound", "Inbound", "Import BIM geometry with height correction", "RMInbound", "R2M_Inbound.svg"),
)
BAR_SVG = "LoopFlow_R2M.svg"
SVG_FILES = (BAR_SVG,) + tuple(item[-1] for item in BUTTONS)
_SVG_ROOT = re.compile(r"<svg\b.*</svg>", re.DOTALL | re.IGNORECASE)


def gid(name: str) -> str:
    return str(uuid.uuid5(NS, name))


def load_svg(name: str) -> str:
    path = TOOLBAR / name
    if not path.is_file():
        raise SystemExit(f"找不到 {path}。請把五個 SVG 放回 toolbar 資料夾再跑。")
    text = path.read_text(encoding="utf-8")
    match = _SVG_ROOT.search(text)
    if not match:
        raise SystemExit(f"{path} 沒有 <svg> 根節點")
    return match.group(0)


def wrap_icon(inner_svg: str) -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" version="1.1" '
        'viewBox="0pt 0pt 48pt 48pt" fill-dark="#FFF" stroke-dark="none">'
        f"{inner_svg}"
        "</svg>"
    )


def icon_xml(key: str, svg_name: str) -> str:
    guid = gid(f"icon.{key}")
    wrapped = wrap_icon(load_svg(svg_name))
    return (
        f'    <icon guid="{guid}" name="{guid}.svg">\n'
        f"      <light>\n        {wrapped}\n      </light>\n"
        f"    </icon>"
    )


def macro_xml(key: str, title: str, help_text: str, command: str) -> str:
    guid = gid(f"macro.{key}")
    bitmap = gid(f"icon.{key}")
    script = f"! _{command}"
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
    bar_bitmap = gid("icon.bar")
    items = []
    order = ["open", "storey", "models", "inbound"]
    for key in order:
        items.append(
            f'      <tool_bar_item guid="{gid(f"item.{key}")}">\n'
            f'        <left_macro_id>{gid(f"macro.{key}")}</left_macro_id>\n'
            f"      </tool_bar_item>"
        )

    macros = "\n".join(
        macro_xml(key, title, help_text, command)
        for key, title, help_text, command, _svg in BUTTONS
    )
    icons = "\n".join(
        [icon_xml("bar", BAR_SVG)]
        + [icon_xml(key, svg_name) for key, _t, _h, _s, svg_name in BUTTONS]
    )

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
    missing = [
        name
        for _k, _t, _h, name, _svg in BUTTONS
        if not (COMMANDS / f"{name}.py").is_file()
    ]
    if missing:
        raise SystemExit("missing command scripts: " + ", ".join(missing))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(xml, encoding="utf-8-sig", newline="\n")
    for name in SVG_FILES:
        path = TOOLBAR / name
        if path.is_file():
            path.unlink()
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes); removed {len(SVG_FILES)} svg files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
