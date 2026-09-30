import tempfile
import unittest
from pathlib import Path

from scripts import sync_user_guide

PAGE = """---
title: สร้าง AI Agent ตัวแรก
description: >-
  วิธีสร้าง
  AI Agent ตัวแรก
---

เริ่มจากเมนู AI Agent

![](../../../assets/step1.png)

   ![](../../../assets/step2.png)



ดู [ทดลองคุย](/guides/ai-agent/try-call)
"""


class SyncUserGuideTests(unittest.TestCase):
    def make_source(self, root: Path) -> Path:
        docs = root / "src" / "content" / "docs"
        (docs / "guides" / "ai-agent").mkdir(parents=True)
        (docs / "overview").mkdir()
        (docs / "en" / "overview").mkdir(parents=True)
        (docs / "guides" / "ai-agent" / "getting-started.md").write_text(PAGE, encoding="utf-8")
        (docs / "guides" / "ai-agent" / "try-call.md").write_text("---\ntitle: ทดลองคุย\n---\n\nเนื้อหา\n", encoding="utf-8")
        (docs / "overview" / "what-is-ingfah.md").write_text(
            "---\ntitle: ingfah คืออะไร?\nsidebar:\n  order: 1\n---\n\nภาพรวม\n", encoding="utf-8"
        )
        (docs / "en" / "overview" / "what-is-ingfah.md").write_text("---\ntitle: What\n---\n\nEN\n", encoding="utf-8")
        (docs / "index.mdx").write_text("---\ntitle: home\n---\n", encoding="utf-8")
        (root / "astro.config.mjs").write_text(
            'link: "guides/ai-agent/try-call",\nlink: "guides/ai-agent/getting-started",\n', encoding="utf-8"
        )
        return root

    def test_sync_writes_clean_pages_and_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = self.make_source(Path(tmp) / "docs")
            dest = Path(tmp) / "out"
            (dest / "stale").mkdir(parents=True)
            pages = sync_user_guide.sync(source, dest)

            self.assertEqual(
                [p.slug for p in pages],
                ["overview/what-is-ingfah", "guides/ai-agent/try-call", "guides/ai-agent/getting-started"],
            )
            self.assertFalse((dest / "stale").exists())
            self.assertFalse((dest / "en").exists())

            page = (dest / "guides" / "ai-agent" / "getting-started.md").read_text(encoding="utf-8")
            self.assertTrue(page.startswith("# สร้าง AI Agent ตัวแรก\n\n> วิธีสร้าง AI Agent ตัวแรก\n"))
            self.assertIn("> Source: https://docs.ingfah.ai/guides/ai-agent/getting-started/", page)
            self.assertNotIn("![](", page)
            self.assertNotIn("\n\n\n", page)
            self.assertIn("(/guides/ai-agent/try-call)", page)

            index = (dest / "INDEX.md").read_text(encoding="utf-8")
            self.assertIn("## ภาพรวม (Overview)", index)
            self.assertIn("- `guides/ai-agent/getting-started.md` — **สร้าง AI Agent ตัวแรก**: วิธีสร้าง AI Agent ตัวแรก", index)

    def test_missing_source_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(SystemExit):
                sync_user_guide.sync(Path(tmp), Path(tmp) / "out")


if __name__ == "__main__":
    unittest.main()
