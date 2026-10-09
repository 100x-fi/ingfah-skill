# Ingfah user guide (คู่มือของอิงฟ้า) — index

A copy of the public Thai user guide at https://docs.ingfah.ai, one file per page.
Do not edit these files by hand; regenerate them with
`python3 scripts/sync_user_guide.py`.
Copied from docs commit efd06de (2026-10-09).

A link inside a page such as `/guides/ai-agent/try-call` is the file
`guides/ai-agent/try-call.md` in this folder, and the public page
`https://docs.ingfah.ai/guides/ai-agent/try-call/`. Screenshots are not copied.

## ภาพรวม (Overview)

- `overview/what-is-ingfah.md` — **ingfah คืออะไร?**: ingfah คือ Agentic CX Platform ที่ช่วยให้ทีม Contact Center ดูแลลูกค้าได้มากขึ้น ภายใต้ทรัพยากรเท่าเดิม
- `overview/why-ingfah.md` — **ทำไมต้อง ingfah?**: สิ่งที่ทำให้ ingfah ต่างจากเจ้าอื่น ทำมาสำหรับตลาดไทยโดยเฉพาะ
- `overview/use-cases.md` — **ตัวอย่างการใช้งาน**: ตัวอย่างการใช้งาน ingfah จริงในธุรกิจ ตั้งแต่รับสายอัตโนมัติไปถึงแคมเปญโทรออก

## บริการ (Services)

- `services/developers.md` — **สำหรับนักพัฒนา**: API ภาษาไทยสำหรับทีมที่ต้องการนำ Voice AI ของ ingfah ไปต่อกับระบบของตัวเอง
- `services/inbound.md` — **รับสาย (Inbound Automation)**: AI Agent รับสายและแชทตลอด 24 ชั่วโมง ส่งต่อเคสพร้อมบริบทครบ ไม่ให้ลูกค้าต้องเล่าซ้ำ
- `services/outbound.md` — **โทรออก (Outbound Campaigns)**: บริหารแคมเปญโทรออกและข้อความอัตโนมัติ ติดตามผล Real-Time โดยไม่เพิ่มต้นทุนคงที่
- `services/platform.md` — **แพลตฟอร์ม**: เทคโนโลยีแกนกลางที่ขับเคลื่อนทุกบริการของ ingfah ตั้งแต่ Voice Cortex ไปถึง Continuous Learning

## แผนงานและมาตรฐาน (Plans & Standards)

- `direction/company-policy.md` — **นโยบายองค์กร**: บริษัท ร้อยเอ็กซ์ จำกัด ผู้พัฒนา ingfah.ai มุ่งมั่นเป็น Trust Infrastructure ที่เชื่อมต่อธุรกิจและลูกค้าเข้าด้วยกัน ผ่าน 4 กลยุทธ์หลักขององค์กร
- `direction/standards.md` — **มาตรฐานและความปลอดภัย**: โครงสร้างพื้นฐาน การปกป้องข้อมูล และมาตรฐานสากลที่ ingfah ดำเนินการและกำลังรับรอง
- `direction/vision.md` — **วิสัยทัศน์**: ingfah ถูกสร้างมาเพื่อกำจัด trilemma ของการบริการลูกค้า ทั้ง scale, personalization และ speed พร้อมกัน

## สำหรับลูกค้าใหม่ (Client Onboarding)

- `onboarding/checklist.md` — **เช็กลิสต์เตรียมความพร้อม**: สิ่งที่ต้องเตรียมก่อนเริ่ม POC กับ ingfah แบ่งเป็นสามหมวด
- `onboarding/timeline.md` — **ไทม์ไลน์**: สามระยะของ ingfah onboarding ตั้งแต่ประชุมครั้งแรกจนถึงลงนามสัญญา รวมประมาณ 40 วัน

## การเชื่อมต่อโทรศัพท์ (Telephony Integration)

- `telephony/overview.md` — **ภาพรวม — เลือกวิธีเชื่อมต่อ**: เปรียบเทียบ IP Peering กับ SIP Registration และการตั้งค่าทิศทาง inbound/outbound
- `telephony/ip-peering.md` — **วิธีที่ 1: IP Peering**: วิธีเชื่อมต่อสำหรับลูกค้าที่มี SBC หรือ public static IP — ตั้งค่าด้วย IP whitelist ไม่มีการลงทะเบียน
- `telephony/sip-registration.md` — **วิธีที่ 2: SIP Registration**: วิธีเชื่อมต่อสำหรับ PBX ทั่วไปที่ไม่มี public IP — Ingfah SIP Server ไป register กับ SIP server ของลูกค้า
- `telephony/faq.md` — **คำถามที่พบบ่อย**: คำถามพบบ่อยเกี่ยวกับการเชื่อมต่อโทรศัพท์กับ ingfah

## แนะนำการใช้งาน (Guides — using the dashboard)

- `guides/menu-overview.md` — **ทำความรู้จักเมนูหลักของเรา**
- `guides/account-login.md` — **เข้าสู่ระบบและจัดการรหัสผ่าน**: วิธีเข้าสู่ระบบ เข้าด้วย SSO ขององค์กร ตั้งรหัสผ่านครั้งแรก และรีเซ็ตรหัสผ่านเมื่อลืม
- `guides/website-announcements.md` — **ดูประกาศและฟีเจอร์ใหม่**: อ่านประกาศที่แสดงบนแดชบอร์ดและเลือกไม่ให้แสดงซ้ำ
- `guides/voice-text-tabs.md` — **สลับแท็บเสียงและข้อความ**: ระบบจำแท็บที่เลือกล่าสุดในหน้า AI Agent ทีม ช่องทางติดต่อ และสายทั้งหมด
- `guides/ai-agent/overview.md` — **ภาพรวม**: สร้างเอเจนต์ AI ที่ทำงานได้ด้วยตนเองและมุ่งเน้นเป้าหมาย ซึ่งใช้การคิดหาเหตุผลคล้ายมนุษย์และเครื่องมือต่างๆ เพื่อส่งมอบผลลัพธ์ที่เหนือกว่า
- `guides/ai-agent/getting-started.md` — **สร้าง AI Agent ตัวแรก**: สร้าง AI Agent ตัวแรก
- `guides/ai-agent/create-text-agent.md` — **สร้าง AI Agent สำหรับแชทข้อความ**: เลือกประเภทข้อความ สร้างแบบร่าง และเตรียม Agent สำหรับตอบแชท
- `guides/ai-agent/how-to-create-agent-flow.md` — **การสร้าง Flow บทสนทนา**: การสร้าง Flow บทสนทนา
- `guides/ai-agent/manage-ai-agent.md` — **ปรับแต่ง AI Agent**: เรียนรู้ระบบแบบร่างและเผยแพร่ของ AI Agent เพื่อแก้ไขและทดสอบโดยไม่กระทบการใช้งานจริง
- `guides/ai-agent/version-history.md` — **ดูประวัติเวอร์ชัน AI Agent**: ตรวจสอบแบบร่างและเวอร์ชันที่เผยแพร่ก่อนหน้า
- `guides/ai-agent/try-call.md` — **ทดลองคุยกับ AI Agent ก่อนใช้งานจริง**: ทดลองคุยกับ AI Agent ก่อนใช้งานจริง
- `guides/ai-agent/delete-ai-agent.md` — **การลบ AI Agent**: วิธีลบแบบร่างและลบ AI Agent ออกจากระบบ
- `guides/ai-agent/prompting-tips.md` — **เทคนิคการสร้าง AI Agent**: เทคนิคการสร้าง AI Agent
- `guides/ai-agent/conversation-control.md` — **ควบคุมทิศทางการสนทนา**: กำหนดจำนวนครั้งการโน้มน้าว จำกัดการถามวน และป้องกันไม่ให้ AI Agent คำนวณวันที่เอง
- `guides/ai-agent/handling-unclear-audio.md` — **รับมือเสียงไม่ชัดและการพูดซ้ำ**: เทคนิคเขียน Prompt ให้ AI Agent รับมือกับเสียงที่ระบบฟังผิด ลูกค้าเงียบ และการพูดประโยคเดิมซ้ำ
- `guides/ai-agent/flow-variables.md` — **การใช้งาน{{ตัวแปร}}**: การใช้งานตัวแปรใน Flow บทสนทนา
- `guides/ai-agent/say-as-pronunciation.md` — **การกำหนดการออกเสียงด้วย <say-as>**: การกำหนดรูปแบบการออกเสียงของ AI Agent สำหรับจำนวนเงิน ตัวเลข เวลา และข้อมูลที่มีวิธีอ่านเฉพาะ
- `guides/ai-agent/ai-agent-tools.md` — **การใช้ Tools ใน AI Agent**: การใช้งาน Tools เพื่อเพิ่มความสามารถให้ AI Agent ระหว่างการสนทนา
- `guides/ai-agent/manage-tools.md` — **สร้างและจัดการ Tools**: สร้าง Tool เพื่อให้ AI Agent เรียกใช้ระบบภายนอกระหว่างสนทนา พร้อมทดสอบการทำงาน
- `guides/ai-agent/ai-agent-visibility.md` — **การตั้งค่าการมองเห็น AI Agent**: การกำหนดสิทธิ์การมองเห็นและการเข้าถึง AI Agent
- `guides/knowledge-base/overview.md` — **ภาพรวมคลังความรู้**: คลังความรู้คืออะไร ทำงานอย่างไร และช่วยให้ AI Agent ตอบคำถามลูกค้าได้แม่นยำขึ้นอย่างไร
- `guides/knowledge-base/writing-faq-documents.md` — **เขียนเอกสาร FAQ ให้ AI Agent ค้นเจอ**: รูปแบบและเทคนิคการเขียนเอกสารคำถามที่พบบ่อย ให้ AI Agent ค้นหาเจอและตอบลูกค้าได้ถูกต้อง
- `guides/knowledge-base/upload-documents.md` — **อัปโหลดและทดสอบการค้นหา**: อัปโหลดไฟล์เข้าคลังความรู้ และทดสอบว่าระบบค้นหาเนื้อหาที่ต้องการได้ก่อนนำไปใช้กับ AI Agent
- `guides/knowledge-base/connect-to-ai-agent.md` — **เชื่อมคลังความรู้กับ AI Agent**: เลือกเอกสารในคลังความรู้ให้ AI Agent ใช้ค้นหาข้อมูลระหว่างสนทนากับลูกค้า
- `guides/knowledge-base/prompting.md` — **เขียน Prompt ให้ AI Agent ใช้คลังความรู้**: เขียน Prompt บอก AI Agent ว่าเมื่อไรต้องค้นหาในคลังความรู้ ค้นหาอย่างไร และนำผลลัพธ์ไปตอบลูกค้าอย่างไร
- `guides/knowledge-base/test-and-improve.md` — **ทดสอบและปรับปรุงคลังความรู้**: ขั้นตอนทดสอบคลังความรู้ทีละหัวข้อ วิธีแก้เมื่อค้นไม่เจอหรือได้คำตอบผิด และเช็กลิสต์ก่อนใช้งานจริง
- `guides/knowledge-base/maintain-documents.md` — **เตรียมข้อมูลและอัปเดตเอกสาร**: แปลงเอกสาร FAQ ที่มีอยู่ให้เป็นเอกสารคลังความรู้ จัดการข้อมูลที่ขัดแย้งหรือยังไม่ยืนยัน และอัปเดตเอกสารโดยไม่เสียคุณภาพเดิม
- `guides/ingfah-skill/overview.md` — **(Beta) ภาพรวม Skill ingfah**: ใช้ ChatGPT หรือ Claude ช่วยสร้าง แก้ไข และดูแล AI Agent บนอิงฟ้า ด้วยภาษาพูดธรรมดา
- `guides/ingfah-skill/install.md` — **ติดตั้งและเชื่อมต่อ Skill ingfah**: ติดตั้ง Skill ingfah ใน Claude หรือ ChatGPT เชื่อมต่อกับบัญชีอิงฟ้าด้วย API Key และอัปเดตเป็นเวอร์ชันล่าสุด
- `guides/ingfah-skill/create-agent.md` — **สร้าง AI Agent ตัวแรกด้วย AI**: บอก AI ว่าต้องการ AI Agent แบบไหน ให้ AI สร้างบนอิงฟ้าให้ แล้วตรวจสอบและทดลองก่อนใช้งานจริง
- `guides/ingfah-skill/examples.md` — **ตัวอย่างการใช้งาน Skill ingfah**: ตัวอย่างข้อความสั่งงาน AI สำหรับแก้ไข AI Agent หาสาเหตุปัญหา ตั้งค่าผลลัพธ์หลังวางสาย คลังความรู้ Tool สายโทรออก รายงาน และ webhook
- `guides/ingfah-skill/automated-testing.md` — **ชุดทดสอบอัตโนมัติ**: ให้ AI ตั้งชุดทดสอบที่จำลองบทสนทนาหลายสิบแบบกับ AI Agent และตรวจผลให้อัตโนมัติทุกครั้งที่แก้ไข
- `guides/ingfah-skill/faq.md` — **คำถามที่พบบ่อยและแก้ไขปัญหา**: คำถามที่พบบ่อยเกี่ยวกับ Skill ingfah และวิธีแก้ปัญหาการติดตั้ง การเชื่อมต่อ และการใช้งาน
- `guides/contact-channels/connect-line-oa.md` — **เชื่อมต่อ LINE Official Account**: เชื่อม LINE OA เข้ากับอิงฟ้า เพื่อให้ทีม AI Agent ตอบแชทลูกค้าผ่าน LINE
- `guides/inbound-outbound/create-ai-agent-team.md` — **สร้างทีม AI Agent**: คู่มือการสร้างและจัดการทีม AI Agent สำหรับระบบโทรเข้าและโทรออก
- `guides/inbound-outbound/team-automations.md` — **ตั้งค่าการทำงานอัตโนมัติของทีม AI Agent**: เลือกให้ทีมทำงานเมื่อเริ่ม ส่งต่อ หรือจบการสนทนา
- `guides/inbound-outbound/multi-agent-team.md` — **ออกแบบทีมหลาย AI Agent**: แนวทางแบ่งงาน ส่งต่อสาย เขียน Prompt ทดสอบ และเปิดใช้งานทีมที่มี AI Agent หลายตัวคุยต่อกันในสายเดียว ให้พร้อมใช้งานจริง
- `guides/inbound-outbound/inbound-set-up.md` — **ตั้งค่า AI Agent ให้รับสายโทรเข้า**: เชื่อมต่อเบอร์โทรศัพท์กับทีม AI Agent เพื่อเริ่มรับสายโทรเข้าอัตโนมัติ
- `guides/inbound-outbound/customer-template.md` — **เทมเพลตข้อมูลลูกค้า**: ตั้งค่าคอลัมน์ข้อมูลลูกค้าที่ใช้ซ้ำในแคมเปญโทรออก
- `guides/inbound-outbound/outbound-batch.md` — **สร้างแคมเปญโทรออก**: วิธีสร้างแคมเปญโทรออกแบบ Batch ด้วย AI Agent ทีละขั้นตอน
- `guides/inbound-outbound/speech-preview.md` — **ฟังตัวอย่างเสียงจากข้อมูลลูกค้า**: ทดสอบว่า AI Agent อ่านค่าในไฟล์ CSV อย่างไรก่อนสร้างแคมเปญโทรออก
- `guides/inbound-outbound/follow-up-calls.md` — **ตั้งค่าโทรติดตามตามเวลาที่ลูกค้าขอ**: เปิดการโทรกลับในแคมเปญโทรออกและตรวจสอบสายที่รอโทรกลับ
- `guides/inbound-outbound/outbound-batch-management.md` — **การจัดการแคมเปญโทรออก (Batch)**: วิธีหยุดชั่วคราว ดำเนินการต่อ และยกเลิกแคมเปญโทรออก
- `guides/inbound-outbound/call-outcome-setup.md` — **ผลลัพธ์หลังจบการสนทนา**: กำหนดและวิเคราะห์ผลลัพธ์ของการสนทนาสำหรับทีม AI Agent ทุกประเภท
- `guides/inbound-outbound/outcome-metadata.md` — **ผลลัพธ์แบบ Metadata (JSON)**: ให้ระบบสรุปข้อมูลจากบทสนทนาออกมาเป็น JSON ตามโครงสร้างที่คุณกำหนด
- `guides/text-chat/connect-line-oa.md` — **เชื่อมต่อ LINE OA ให้ AI Agent ตอบแชท**: เพิ่มช่องทางติดต่อ LINE OA และเลือกทีม AI Agent ที่จะตอบแชทลูกค้าอัตโนมัติ
- `guides/text-chat/chat-sessions.md` — **จัดการแชทกับลูกค้า**: ติดตามแชทที่ AI Agent ตอบ รับช่วงตอบเอง มอบหมายผู้ดูแล และปิดการสนทนา
- `guides/text-chat/text-analytics.md` — **แดชบอร์ดแชทข้อความ**: ดูภาพรวมการตอบแชท จำนวนลูกค้า ผลลัพธ์ และช่วงเวลาที่มีข้อความมากที่สุด
- `guides/inbound-outbound/all-calls.md` — **สายและแชททั้งหมด**: ค้นหา กรอง และส่งออกประวัติการโทรและแชทข้อความ
- `guides/reports/text-analytics.md` — **ดูสถิติแชทข้อความ**: อ่านผลรวม แนวโน้มรายชั่วโมง และช่วงเวลาที่ลูกค้าส่งข้อความมาก
- `guides/reports/voice-heatmap.md` — **ดูช่วงเวลาที่มีสายโทรมาก**: ใช้แผนภูมิความร้อนในแดชบอร์ดวิเคราะห์จำนวนสายตามวันและชั่วโมง
- `guides/settings/user-roles.md` — **สิทธิ์ผู้ใช้งาน**: ทำความเข้าใจสิทธิ์ Owner และ Operator ว่าแต่ละสิทธิ์เข้าถึงอะไรได้บ้าง พร้อมวิธีให้สิทธิ์ Guest แบบชั่วคราว
- `guides/settings/api-keys.md` — **API Keys**: สร้างและจัดการ API Key สำหรับเชื่อมต่อระบบภายนอกเข้ากับแพลตฟอร์มอิงฟ้า
- `guides/settings/billing.md` — **บิลและการใช้งาน**: ดูโควต้าตามแพ็กเกจ ปริมาณการใช้งานในรอบบิล และดาวน์โหลดใบแจ้งหนี้/ใบเสร็จ
- `guides/settings/data-retention.md` — **การเก็บรักษาข้อมูล (Data Retention)**: ตั้งค่าระยะเวลาเก็บไฟล์เสียงและข้อมูลการสนทนา ดูประวัติการลบข้อมูล และขอใบรับรองการเก็บรักษาข้อมูล
- `guides/settings/activity-logs.md` — **ประวัติการใช้งาน (Activity Logs)**: ตรวจสอบว่าใครทำอะไรในระบบเมื่อไหร่ สำหรับงานตรวจสอบภายใน

## บันทึกการอัปเดต (Release Notes)

- `release-notes.md` — **Release Notes**: สรุปรายการอัปเดต ฟีเจอร์ใหม่ การปรับปรุงประสิทธิภาพ และการแก้ไขข้อบกพร่องของแพลตฟอร์ม ingfah
