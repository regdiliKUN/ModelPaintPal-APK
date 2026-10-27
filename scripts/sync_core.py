# -*- coding: utf-8 -*-
"""把桌面版（Windows）的核心层同步进安卓仓库。

安卓端只重写了界面（Kivy），配色匹配、配方计算、数据库这些纯 Python 逻辑
仍然由桌面版仓库提供。与其复制一份慢慢跑偏，不如每次构建前同步进来 ——
`app/` 已在 .gitignore 里，不进版本库。

用法：

    python scripts/sync_core.py                    # 取同级目录的桌面版仓库
    python scripts/sync_core.py --from <app 目录>  # 指定桌面版的 app 目录
    python scripts/sync_core.py --from-git         # 从 GitHub 浅克隆（干净环境用）

同步完成后 `python main.py` 或 `buildozer android debug` 就能跑。
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEST = REPO_ROOT / "app"
DESKTOP_REPO = "https://github.com/regdiliKUN/ModelPaintPal.git"
# 桌面版仓库里的 app 包位置
LOCAL_CANDIDATES = (
    REPO_ROOT.parent / "ModelPaintPal" / "src" / "ModelPaintPal" / "app",
    REPO_ROOT.parent / "src" / "ModelPaintPal" / "app",
)


def _copy(src: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(
        src, dest,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"),
    )


def _from_git() -> Path:
    tmp = Path(tempfile.mkdtemp(prefix="mpp-core-"))
    print(f"浅克隆桌面版仓库 → {tmp}")
    subprocess.run(
        ["git", "clone", "--depth", "1", DESKTOP_REPO, str(tmp / "repo")],
        check=True,
    )
    return tmp / "repo" / "src" / "ModelPaintPal" / "app"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="同步桌面版核心层到安卓仓库")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--from", dest="src", help="桌面版的 app 目录路径")
    g.add_argument("--from-git", action="store_true", help="从 GitHub 浅克隆")
    args = ap.parse_args(argv)

    if args.from_git:
        src = _from_git()
    elif args.src:
        src = Path(args.src).expanduser().resolve()
    else:
        src = next((p for p in LOCAL_CANDIDATES if p.is_dir()), None)
        if src is None:
            print("找不到桌面版仓库，请用 --from 指定 app 目录，或用 --from-git。",
                  file=sys.stderr)
            return 2

    src = Path(src)
    if not (src / "__init__.py").is_file():
        print(f"{src} 不像桌面的 app 包（缺 __init__.py）", file=sys.stderr)
        return 2

    _copy(src, DEST)

    files = sum(1 for _ in DEST.rglob("*.py"))
    print(f"已同步 {files} 个 .py → {DEST}")
    print("提示：app/ui 与 app/resources 是 Qt 界面，进 APK 时会被 buildozer 排除。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
