# เชื่อมต่อ LINE Official Account

> เชื่อม LINE OA เข้ากับอิงฟ้า เพื่อให้ทีม AI Agent ตอบแชทลูกค้าผ่าน LINE
>
> Source: https://docs.ingfah.ai/guides/contact-channels/connect-line-oa/

เมื่อเชื่อม **LINE Official Account (LINE OA)** แล้ว ข้อความที่ลูกค้าส่งเข้า LINE OA จะเข้ามาที่อิงฟ้า และทีม AI Agent ที่คุณเลือกจะเป็นคนตอบ

## สิ่งที่ต้องเตรียม

- สิทธิ์ Admin ของ LINE OA ใน [LINE Official Account Manager](https://manager.line.biz)
- สิทธิ์เข้า [LINE Developers Console](https://developers.line.biz/console/) ด้วยบัญชีเดียวกัน
- ทีม AI Agent แบบข้อความ ถ้ายังไม่มี ข้ามไปก่อนได้แล้วค่อยเลือกทีมทีหลัง

ข้อมูลที่ต้องเอามาใส่ในอิงฟ้ามี 3 ค่า:

| ค่า | หาได้ที่ |
|-----|---------|
| Channel Secret (ความลับแชนแนล) | LINE Official Account Manager (ขั้นตอนที่ 1) |
| Channel Access Token | LINE Developers Console (ขั้นตอนที่ 2) |
| LINE ID | LINE Official Account Manager ใต้ชื่อบัญชี ขึ้นต้นด้วย `@` |

## ขั้นตอนที่ 1: เปิด Messaging API และคัดลอก Channel Secret

1. เข้า [LINE Official Account Manager](https://manager.line.biz) แล้วเลือก LINE OA ที่จะเชื่อม
2. กด **ตั้งค่า** มุมขวาบน → เมนูซ้าย **Messaging API**
3. ถ้ายังไม่เคยเปิด กดเปิดใช้ Messaging API แล้วเลือก Provider ที่มีอยู่หรือสร้างใหม่ ช่อง Privacy Policy และ Terms of Use เว้นว่างได้
4. ที่ **ความลับแชนแนล** กด **คัดลอก** แล้วเก็บไว้

## ขั้นตอนที่ 2: ออก Channel Access Token

1. เข้า [LINE Developers Console](https://developers.line.biz/console/)
2. เลือก Provider จากขั้นตอนที่ 1 → เลือก Channel ที่ชื่อตรงกับ LINE OA
3. เปิดแท็บ **Messaging API** แล้วเลื่อนลงล่างสุด
4. ที่ **Channel access token (long-lived)** กด **Issue** แล้วคัดลอกเก็บไว้

:::caution[เก็บ Token และ Secret เป็นความลับ]
ใครได้ 2 ค่านี้ไปจะส่งข้อความในนาม LINE OA ของคุณได้ ห้ามส่งต่อหรือโพสต์ในที่สาธารณะ
:::

## ขั้นตอนที่ 3: เพิ่มช่องทาง LINE ในอิงฟ้า

1. ล็อกอินที่ https://ingfah.ai/login
2. เมนูด้านซ้าย → **ช่องทางติดต่อ** → แท็บ **ข้อความ**
3. กด **เพิ่มช่องทางติดต่อ**
4. กรอกข้อมูล:
   - **แพลตฟอร์ม**: เลือก **LINE OA** (แก้ภายหลังไม่ได้)
   - **ชื่อช่องทาง**: ชื่อที่ทีมคุณจำได้ เช่น `LINE สาขาสยาม`
   - **Channel Access Token**: วางค่าจากขั้นตอนที่ 2
   - **Channel Secret**: วางค่าจากขั้นตอนที่ 1
   - **LINE ID**: ใส่เฉพาะตัวอักษรหลัง `@` เพราะช่องนี้มี `@` ให้แล้ว
   - **ทีม AI Agent ที่รับผิดชอบ**: เลือกทีมที่จะตอบแชทในช่องทางนี้
5. กด **เพิ่มช่องทางติดต่อ**
6. ในหน้ารายละเอียดช่องทาง กดคัดลอก **Webhook URL**

## ขั้นตอนที่ 4: ใส่ Webhook URL ใน LINE

อิงฟ้าไม่ได้ตั้ง Webhook ใน LINE ให้อัตโนมัติ ต้องวางเองขั้นตอนนี้

1. กลับไปที่ [LINE Official Account Manager](https://manager.line.biz) → **ตั้งค่า** → **Messaging API** หน้าเดียวกับขั้นตอนที่ 1
2. ที่ **ลิงก์ Webhook** วาง Webhook URL จากอิงฟ้า → กด **บันทึก**

## ขั้นตอนที่ 5: เปิด Webhook และปิดข้อความตอบกลับอัตโนมัติ

ถ้าไม่ปิดข้อความตอบกลับอัตโนมัติ ลูกค้าจะได้คำตอบซ้ำทั้งจาก LINE และจาก AI Agent

1. เมนูซ้าย **ตั้งค่าการตอบกลับ**
2. เปิด **Webhook**
3. ปิด **ข้อความตอบกลับอัตโนมัติ**

## ทดสอบ

ส่งข้อความหา LINE OA จากโทรศัพท์ของคุณ แล้วดูว่า:

- AI Agent ตอบกลับใน LINE
- แชทนั้นขึ้นในอิงฟ้า

## แก้ปัญหาเบื้องต้น

| อาการ | ตรวจที่ |
|-------|--------|
| ข้อความไม่เข้าอิงฟ้า | Webhook URL วางครบทั้งบรรทัดและเปิด **Webhook** ใน **ตั้งค่าการตอบกลับ** แล้ว |
| ข้อความเข้าอิงฟ้าแต่ AI Agent ไม่ตอบ | ช่องทางนี้เลือก **ทีม AI Agent ที่รับผิดชอบ** แล้ว |
| ลูกค้าได้คำตอบ 2 ครั้ง | ปิด **ข้อความตอบกลับอัตโนมัติ** ตามขั้นตอนที่ 5 แล้ว |
| ออก Token ใหม่ใน LINE แล้วแชทหยุด | แก้ช่องทางในอิงฟ้า ใส่ **Channel Access Token** ตัวใหม่ |
