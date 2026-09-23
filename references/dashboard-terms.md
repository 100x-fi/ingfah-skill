# Dashboard terms by area

The main entity table lives in `SKILL.md`. These are the field-level names
the dashboard uses in each area, for when the user names a field rather than
an entity. Answer in their words.

## Postprocessors

The dashboard does not use the word "postprocessor". All four live under
**Set post-call results / ตั้งค่าผลลัพธ์หลังวางสาย** on the team page.

| API | Dashboard (EN) | Dashboard (TH) |
|---|---|---|
| `type: disposition` | Disposition Outcome / Conversation Outcome | ผลลัพธ์แบบสถานะ / ผลลัพธ์หลังจบการสนทนา |
| `disposition_outcomes[].outcome` | Outcome name | ชื่อผลลัพธ์ |
| `disposition_outcomes[].prompt` | Outcome classification criteria | เกณฑ์การจำแนกผลลัพธ์ |
| `type: outcome_metadata` | Outcome Metadata (JSON) | ผลลัพธ์แบบ metadata (JSON) |
| `json_schema.name` | Schema name / the data set | ชื่อชุดข้อมูล |
| `instruction` | Instruction | คำสั่ง |
| `is_enabled` | On / Off | เปิด / ปิด |
| `type: summary` | Conversation summary (Auto) | สรุปบทสนทนา (อัตโนมัติ) |
| `disposition_outcome` on a record | Result | ผลลัพธ์ |
| `outcome_metadata` on a record | Metadata | Metadata |

## Agent prompt fields

| API field | Dashboard (EN) | Dashboard (TH) |
|---|---|---|
| `name` | AI Agent Name — what it calls itself on the call | ชื่อ AI Agent |
| `vocal_name` | Agent vocal name — what staff and other agents call it | Agent vocal name |
| `greeting_message` | Initial Greeting Message | ข้อความทักทายเริ่มต้น |
| `ai_instruction_identity` | Identity | ตัวตน |
| `ai_instruction_task` | Task | เป้าหมาย/หน้าที่ |
| `ai_instruction_flow` | Agent Flow | Agent Flow |
| `voice_id` | Voice | เสียง |

## Tool fields

| API field | Dashboard (EN) | Dashboard (TH) |
|---|---|---|
| `signature` | Signature | Signature |
| `description` | Description for AI Agent | คำอธิบายสำหรับ AI Agent |
| `parameters` | Function Parameters | Function Parameters |
| `integration` | Integration Type | ประเภท Integration |
| `integration_parameters` | Integration Parameters | Integration Parameters |

## Batch and record status words

Batch tabs: In Progress / กำลังดำเนินการ, Paused / หยุดชั่วคราว,
Scheduled / รอดำเนินการ, Completed / สิ้นสุด.

Record statuses: Called / โทรแล้ว, Pending / รอโทร, Calling / กำลังสนทนา,
Missed / ไม่รับสาย, Busy / สายไม่ว่าง, Case Not Closed / ปิดเคสไม่ได้,
Error / ผิดพลาด, Do Not Contact / ไม่ติดต่อ.
