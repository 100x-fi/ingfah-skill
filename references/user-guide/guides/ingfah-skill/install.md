# ติดตั้งและเชื่อมต่อ Skill ingfah

> ติดตั้ง Skill ingfah ใน Claude หรือ ChatGPT เชื่อมต่อกับบัญชีอิงฟ้าด้วย API Key และอัปเดตเป็นเวอร์ชันล่าสุด
>
> Source: https://docs.ingfah.ai/guides/ingfah-skill/install/

## ขั้นตอนที่ 1: ติดตั้ง Skill

Skill ของอิงฟ้าเผยแพร่อย่างเป็นทางการบน [skills.sh](https://skills.sh/100x-fi/ingfah-skill/ingfah) ซึ่งเป็นแหล่งรวม Skill สำหรับ AI วิธีติดตั้งจะต่างกันตามแอปที่คุณใช้

### สำหรับ Claude Desktop app

Claude Desktop app ติดตั้ง Skill ด้วยการอัปโหลดไฟล์ .zip

1. ดาวน์โหลดไฟล์ Skill ที่ [ingfah-skill v1.8.0 (.zip)](https://github.com/100x-fi/ingfah-skill/archive/refs/tags/v1.8.0.zip) **ไม่ต้องแตกไฟล์**
2. เปิด Claude Desktop app แล้วไปที่ **Settings → Capabilities**
3. ตรวจสอบว่าเปิด **Code execution and file creation** ไว้แล้ว เพราะ Skill ต้องใช้ความสามารถนี้
4. ในส่วน **Skills** กด **Upload skill** แล้วเลือกไฟล์ .zip ที่ดาวน์โหลดมา
5. เปิดใช้งาน Skill **ingfah** แล้ว **เริ่มแชทใหม่**

:::note
Skill ที่อัปโหลดจะผูกกับบัญชี Claude ของคุณ จึงใช้ได้ทั้งใน Claude Desktop app และ claude.ai บนเว็บ
:::

### สำหรับ ChatGPT Desktop app และ Claude Code

คุณไม่จำเป็นต้องเปิดโปรแกรมอื่นหรือพิมพ์คำสั่งเอง เพียงให้ AI ติดตั้งให้

1. เปิด ChatGPT Desktop app หรือ Claude Code
2. เริ่มแชทใหม่ แล้วคัดลอกข้อความด้านล่างไปวางในช่องแชท

:::tip[พิมพ์ข้อความนี้ให้ AI]
ช่วยติดตั้ง Skill ingfah จาก skills.sh ให้หน่อย โดยใช้คำสั่ง `npx skills add 100x-fi/ingfah-skill -g`
:::

3. หาก AI ขออนุญาตรันคำสั่ง ให้กด **อนุญาต** (Allow)
4. เมื่อ AI แจ้งว่าติดตั้งเสร็จแล้ว ให้ **ปิดแชทนี้แล้วเริ่มแชทใหม่** เพื่อให้ AI โหลด Skill ที่เพิ่งติดตั้ง

:::note[สำหรับผู้ที่คุ้นเคยกับ Terminal]
สามารถติดตั้งเองได้ด้วยคำสั่ง

```bash
npx skills add 100x-fi/ingfah-skill -g
```
:::

## ขั้นตอนที่ 2: สร้าง API Key และเชื่อมต่อกับอิงฟ้า

AI จะเชื่อมต่อกับระบบอิงฟ้าผ่าน **API Key** ของคุณ

1. ล็อกอินเข้าระบบที่ https://ingfah.ai/login
2. ที่เมนูด้านซ้ายมือ เลือก **การตั้งค่า** → **API Keys**
3. กดปุ่ม **สร้าง API Key**
4. ตั้งชื่อ API Key ให้จำง่าย เช่น `Claude Desktop` แล้วกด **สร้าง**
5. ระบบจะแสดง API Key ขึ้นมา ให้กด **คัดลอก** แล้วเก็บไว้ในที่ปลอดภัย

:::danger[API Key จะแสดงเพียงครั้งเดียวเท่านั้น]
หลังจากปิดหน้าต่างนี้ไปแล้วจะไม่สามารถดู API Key เดิมได้อีก หากทำหาย ให้สร้าง API Key ใหม่แล้วลบอันเก่าทิ้ง

API Key เปรียบเสมือนรหัสผ่าน **ห้ามส่งต่อให้ผู้อื่น** และห้ามโพสต์ในที่สาธารณะ
:::

จากนั้นกลับไปที่แชทใหม่ใน AI แล้วพิมพ์:

:::tip[พิมพ์ข้อความนี้ให้ AI]
ช่วยเชื่อมต่อกับ ingfah ให้หน่อย
:::

AI จะขอ **API Key** ให้วาง API Key ที่คัดลอกไว้ลงในช่องแชท แล้วทำตามคำแนะนำบนหน้าจอจนเชื่อมต่อสำเร็จ

แนะนำให้**แยก API Key สำหรับแอป AI โดยเฉพาะ** และลบทิ้งทันทีเมื่อเลิกใช้ ดูแนวปฏิบัติเพิ่มเติมที่ [API Keys](/guides/settings/api-keys/)

เมื่อเชื่อมต่อสำเร็จแล้ว ไปต่อที่ [สร้าง AI Agent ตัวแรกด้วย AI](/guides/ingfah-skill/create-agent/)

## อัปเดต Skill เป็นเวอร์ชันล่าสุด

Skill ingfah มีการปรับปรุงอย่างต่อเนื่อง ดูสิ่งที่เปลี่ยนในแต่ละเวอร์ชันได้ที่ [Release ของ ingfah-skill](https://github.com/100x-fi/ingfah-skill/releases)

[เวอร์ชัน 1.8.0](https://github.com/100x-fi/ingfah-skill/releases/tag/v1.8.0) เพิ่มคำแนะนำในการเลือกการตั้งค่า วางแผนทดลองใช้งาน และวัดผลตามเป้าหมายธุรกิจ พร้อมอัปเดตคู่มือที่ AI ใช้อ้างอิง เพิ่ม API สำหรับตรวจว่ายังรับสายโทรเข้าได้หรือไม่ ดูแท็กลูกค้าในแชท และตรวจตัวเลือก Automation ของทีม

หากต้องการตรวจจำนวนสายที่ระบบยังรับได้ ให้ API Key มีสิทธิ์ `inbound_admission:read` ส่วนการดูแท็กลูกค้าใช้ `chat_sessions:read` และการดูตัวเลือก Automation ใช้ `client_products:read` ดูวิธีจัดการสิทธิ์ที่ [API Keys](/guides/settings/api-keys/)

- **Claude Desktop app** ดาวน์โหลดไฟล์ .zip เวอร์ชันล่าสุดจากลิงก์ในขั้นตอนที่ 1 แล้วไปที่ **Settings → Capabilities → Skills** ลบ Skill ingfah เดิมออก แล้วอัปโหลดไฟล์ใหม่
- **ChatGPT Desktop app และ Claude Code** พิมพ์ให้ AI ติดตั้งซ้ำด้วยข้อความเดิมในขั้นตอนที่ 1 ระบบจะดึงเวอร์ชันล่าสุดมาให้

หลังอัปเดตแล้ว ให้**เริ่มแชทใหม่**ทุกครั้ง

:::tip[ตรวจสอบเวอร์ชันที่ใช้อยู่]
Skill ingfah ที่ติดตั้งอยู่เป็นเวอร์ชันอะไร
:::
