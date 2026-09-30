import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from scripts import faq_lint

GOOD = """## หมวด 1: การชำระเงิน

### Q: ระบบตัดเงินวันไหน / ตัดยอดวันที่เท่าไหร่

**คำถามที่เข้าข่ายหัวข้อนี้:** ตัดเงินวันไหน, ตัดยอดวันที่เท่าไหร่, เงินไม่พอตัด

ระบบตัดเงินค่าบริการตัวอย่างวันไหน: ตัดอัตโนมัติทุกวันที่ 5 ของเดือน [ตัวเลขคงที่]

---

### Q: ติดต่อเจ้าหน้าที่ยังไง / เบอร์คอลเซ็นเตอร์

ช่องทางติดต่อเจ้าหน้าที่ตัวอย่าง: โทร 02-000-0000 เวลา 08:30 ถึง 17:30 น. [เบอร์และเวลาทำการคงที่]

---
"""


def findings_for(text):
    _, _, findings = faq_lint.check(text.split("\n"))
    return findings


def messages(findings, level=None):
    return [f.message for f in findings if level is None or f.level == level]


class FaqLintTests(unittest.TestCase):
    def test_well_formed_file_is_clean(self):
        self.assertEqual(findings_for(GOOD), [])

    def test_missing_entries_is_an_error(self):
        findings = findings_for("ข้อความทั่วไป ไม่มีหัวข้อคำถาม\n")
        self.assertTrue(any("no `### Q:` entries" in m for m in messages(findings, "error")))

    def test_table_reported_once_as_error(self):
        text = GOOD + "\n| อายุ | เบี้ย |\n|---|---|\n| 20 | 1.2% |\n"
        errors = [m for m in messages(findings_for(text), "error") if m.startswith("table")]
        self.assertEqual(len(errors), 1)

    def test_author_notes_and_placeholders_are_errors(self):
        for line in ["<!-- ยืนยันตัวเลข -->", "TODO ตรวจอีกครั้ง", "สายด่วน โทร XXXX", "หมายเหตุผู้เขียน: แก้ตามฉบับ 3"]:
            with self.subTest(line=line):
                text = GOOD.replace("[ตัวเลขคงที่]", "[ตัวเลขคงที่]\n" + line)
                self.assertTrue(messages(findings_for(text), "error"))
        text = GOOD.replace("ติดต่อเจ้าหน้าที่ยังไง", "<คำถามแบบที่ลูกค้าพูด>")
        self.assertTrue(any("placeholder" in m for m in messages(findings_for(text), "error")))

    def test_say_as_tag_is_not_a_placeholder(self):
        text = GOOD.replace("ทุกวันที่ 5", '<say-as interpret-as="date">5</say-as>')
        self.assertFalse(any("placeholder" in m for m in messages(findings_for(text))))

    def test_hyphen_ranges_flagged_but_phone_numbers_are_not(self):
        text = GOOD.replace("08:30 ถึง 17:30", "08:30-17:30").replace("ทุกวันที่ 5", "อายุ 61-65 ปี")
        ranges = [m for m in messages(findings_for(text)) if m.startswith("range")]
        self.assertEqual(len(ranges), 2)
        self.assertFalse(any("02-000" in m for m in ranges))

    def test_cross_reference_and_filler_warnings(self):
        text = GOOD.replace("[ตัวเลขคงที่]", "[ตัวเลขคงที่] ช่องทางเดียวกับหัวข้อด้านบน สอบถามได้เลยนะคะ")
        warnings = messages(findings_for(text), "warning")
        self.assertTrue(any("ด้านบน" in m for m in warnings))
        self.assertTrue(any("สอบถามได้เลย" in m for m in warnings))

    def test_missing_restatement_line(self):
        text = GOOD.replace("ระบบตัดเงินค่าบริการตัวอย่างวันไหน: ตัด", "ตัด")
        self.assertTrue(any("restate the question" in m for m in messages(findings_for(text), "warning")))

    def test_unclosed_entry_and_non_q_heading(self):
        text = GOOD.replace("[ตัวเลขคงที่]\n\n---", "[ตัวเลขคงที่]", 1) + "\n### คำถามไม่มี Q\n"
        warnings = messages(findings_for(text), "warning")
        self.assertTrue(any("not closed" in m for m in warnings))
        self.assertTrue(any("`### Q: <question>` form" in m for m in warnings))

    def test_duplicate_phrasing_across_entries(self):
        text = GOOD.replace("เบอร์คอลเซ็นเตอร์", "ตัดยอดวันที่เท่าไหร่")
        self.assertTrue(any("also heads the entry" in m for m in messages(findings_for(text), "warning")))

    def test_long_entry_and_stranded_answer_lines(self):
        detail = "\n".join(f"รายละเอียดข้อที่ {i} ของการตัดเงินค่าบริการตัวอย่างเพิ่มเติมสำหรับลูกค้าทุกกลุ่ม" for i in range(1, 16))
        text = GOOD.replace("[ตัวเลขคงที่]", "[ตัวเลขคงที่]\n" + detail, 1)
        warnings = messages(findings_for(text), "warning")
        self.assertTrue(any("more than one chunk holds" in m for m in warnings))
        self.assertTrue(any("without this entry's question or restatement" in m for m in warnings))

    def test_stranded_lines_that_name_their_subject_are_not_flagged(self):
        filler = "\n".join(f"รายละเอียดข้อที่ {i} ของการตัดเงินค่าบริการตัวอย่างเพิ่มเติมสำหรับลูกค้าทุกกลุ่ม" for i in range(1, 11))
        tail = "\n".join(f"{i}. ช่องทางติดต่อเจ้าหน้าที่ตัวอย่างช่องทางที่ {i}: โทร 02-000-000{i} เวลา 08:30 ถึง 17:30 น." for i in range(1, 9))
        text = GOOD.replace("[ตัวเลขคงที่]", "[ตัวเลขคงที่]\n" + filler + "\n" + tail, 1)
        stranded = [m for m in messages(findings_for(text), "warning") if "do not name their subject" in m]
        self.assertTrue(stranded)
        self.assertFalse(any("ช่องทางที่" in text.split("\n")[f.line - 1] for f in findings_for(text) if "do not name" in f.message))

    def test_ingest_removes_spaces_between_thai_letters_only(self):
        self.assertEqual(faq_lint.ingest_line("  ผูกบัญชี   ไม่ได้ / LINE  @example "), "ผูกบัญชีไม่ได้ / LINE @example")

    def test_chunks_pack_to_limit_without_overlap(self):
        lines = ["ก" * 200 + "." for _ in range(10)]
        chunks = faq_lint.simulate_chunks(lines)
        self.assertGreater(len(chunks), 1)
        for chunk in chunks:
            self.assertLessEqual(chunk.tokens, faq_lint.CHUNK_TOKENS)
        seen = [s.line for c in chunks for s in c.sentences]
        self.assertEqual(seen, sorted(set(seen)))

    def test_cli_exit_status_and_compare(self):
        with tempfile.TemporaryDirectory() as tmp:
            good = Path(tmp) / "faq.md"
            good.write_text(GOOD, encoding="utf-8")
            old = Path(tmp) / "old.md"
            old.write_text(GOOD, encoding="utf-8")
            stripped = Path(tmp) / "new.md"
            stripped.write_text(GOOD.replace(" [ตัวเลขคงที่]", "").replace(" [เบอร์และเวลาทำการคงที่]", ""), encoding="utf-8")
            bad = Path(tmp) / "bad.md"
            bad.write_text("| a | b |\n", encoding="utf-8")

            out = io.StringIO()
            with redirect_stdout(out):
                self.assertEqual(faq_lint.main([str(good)]), 0)
                self.assertEqual(faq_lint.main([str(bad)]), 1)
                faq_lint.main([str(stripped), "--compare", str(old), "--chunks"])
            self.assertIn("[คงที่] tags: 2 -> 0  <- dropped", out.getvalue())
            self.assertIn("chunk 1: lines", out.getvalue())


if __name__ == "__main__":
    unittest.main()
