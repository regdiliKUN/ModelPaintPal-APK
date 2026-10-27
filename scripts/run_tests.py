# -*- coding: utf-8 -*-
"""跑安卓端单元测试。

Kivy 会把 stdout 接管掉（`-m unittest` 的进度经常整个消失），所以这里自己
收集文本再落盘。跑之前先 `python scripts/sync_core.py` 同步桌面版核心层。

    python scripts/run_tests.py
"""

from __future__ import annotations

import io
import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "test-report.txt"

os.environ.setdefault("KIVY_NO_CONSOLELOG", "1")
os.environ.setdefault("KIVY_NO_ARGS", "1")
sys.path.insert(0, str(ROOT))

if not (ROOT / "app" / "__init__.py").is_file():
    raise SystemExit("缺少 app/ 核心层，先跑 python scripts/sync_core.py")

TESTS = str(ROOT / "mobile" / "tests")
suite = unittest.TestLoader().discover(
    TESTS, pattern="test_*.py", top_level_dir=TESTS)

buf = io.StringIO()
result = unittest.TextTestRunner(stream=buf, verbosity=2).run(suite)
buf.write("\n== summary: run=%d fail=%d error=%d ==\n"
          % (result.testsRun, len(result.failures), len(result.errors)))

OUT.write_text(buf.getvalue(), encoding="utf-8")
os.write(1, ("tests=%d fail=%d error=%d -> %s\n"
             % (result.testsRun, len(result.failures), len(result.errors),
                OUT)).encode())
sys.exit(0 if result.wasSuccessful() else 1)
