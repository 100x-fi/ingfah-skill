# วิธีที่ 2: SIP Registration

> วิธีเชื่อมต่อสำหรับ PBX ทั่วไปที่ไม่มี public IP — Ingfah SIP Server ไป register กับ SIP server ของลูกค้า
>
> Source: https://docs.ingfah.ai/telephony/sip-registration/

## หลักการทำงาน

Ingfah SIP Server จะทำตัวเป็น SIP client ที่ลงทะเบียน (REGISTER) กับ SIP server ของลูกค้าโดยอัตโนมัติ เมื่อมีสายเข้ามาที่ DID ระบบของลูกค้าจะส่ง INVITE มาที่ Ingfah SIP Server ผ่าน registration session ที่ active อยู่ วิธีนี้เหมาะกับ PBX ทั่วไปที่ไม่มี public static IP

### การลงทะเบียน (Background session)

### สายเข้า (Inbound)

### สายออก (Outbound)

## ข้อมูลที่ต้องเตรียม

| ฟิลด์ | จำเป็น | คำอธิบาย | ตัวอย่าง / default |
|---|---|---|---|
| `name` | ✓ | ชื่อย่อใช้แทน trunk นี้ (ตัวอักษรอังกฤษ ไม่มีช่องว่าง) | `"abc-corp"` |
| `server` | ✓ | SIP registrar — IP สาธารณะหรือ FQDN | `"sip.example.com"` |
| `proxy` | — | Outbound proxy (ระบุเฉพาะถ้าต่างจาก `server`) | default = `server` |
| `port` | — | SIP signaling port | default `5060` |
| `transport` | — | `"udp"` หรือ `"tls"` (ปลอดภัยกว่า ต้องใช้ cert) | default `"udp"` |
| `codec` | — | Array ของ codec ตามลำดับ: `["g722","ulaw"]` (**แนะนำ**) หรือ `["ulaw"]` | default `["g722","ulaw"]` |
| `sip_user` | ✓ | SIP identity — ที่ Ingfah ใช้ register (`From:`, `Contact:`, registration URI) | `"020256960"` หรือ `"101"` |
| `auth_user` | — | Username ใน `Authorization` header (ระบุเฉพาะถ้าต่างจาก `sip_user` เช่น MS Teams) | default = `sip_user` |
| `password` | ✓ | SIP password คู่กับ `auth_user` | — |
| `number` | — | หมายเลข PSTN หรือ extension; routing key สำหรับโทรออก ถ้าต่างจาก `sip_user` ให้ระบุ | default = `sip_user` |
| `direction` | — | `"inbound"`, `"outbound"`, หรือ `"both"` | default `"both"` |

:::tip[กรณี sip_user ต่างจาก PSTN number]
เช่น PBX ของลูกค้า map extension `"101"` → DID `"021243449"` ให้ระบุ `sip_user: "101"` และ `number: "021243449"` แยกกัน
:::

## สิ่งที่ลูกค้าต้องทำในระบบของตน

- สร้าง **SIP Extension / Trunk Account** สำหรับ Ingfah SIP Server พร้อม username + password
- อนุญาตให้ลงทะเบียนจาก Ingfah SIP Server IP (ดู endpoint ที่ทีมงานส่งให้) ถ้าระบบจำกัด IP
- ตั้ง **Inbound Routing** ให้สายที่เข้ามาที่ DID route ไปที่ extension นี้
- หากระบบมี **NAT**: ตรวจสอบว่า `Contact` header ส่งเป็น IP สาธารณะ

:::caution[หาก register ไม่ติด]
ทั้ง inbound และ outbound จะใช้งานไม่ได้ ตรวจสอบว่า Ingfah SIP Server ลงทะเบียนสำเร็จจากฝั่งลูกค้าก่อนทดสอบสาย
:::

## แบบฟอร์มเชื่อมต่อ

กรุณา copy ฟอร์มด้านล่าง กรอกข้อมูลให้ครบ แล้วส่งกลับให้ทีมงาน

```text
========== SIP REGISTRATION TRUNK ==========
ชื่อบริษัท/โครงการ  : ____________________
ผู้ติดต่อ           : ____________________
อีเมล / เบอร์โทร  : ____________________

[ข้อมูลทางเทคนิค]
name       : ____________________   (ชื่อย่อ ภาษาอังกฤษ)
server     : ____________________   (SIP registrar — host / IP)
proxy      : ____________________   (ระบุเฉพาะถ้าต่างจาก server)
port       : ____________________   (default 5060)
transport  : [  ] udp   [  ] tls
codec      : [  ] g722 (แนะนำ)  [  ] ulaw
sip_user   : ____________________   (SIP identity — ที่ Ingfah ใช้ register)
auth_user  : ____________________   (ระบุเฉพาะถ้าต่างจาก sip_user)
password   : ____________________
number     : ____________________   (ระบุเฉพาะถ้าต่างจาก sip_user)

[ทิศทางการใช้งาน]
direction  : [  ] inbound   [  ] outbound   [  ] both (default)

[ฝั่งลูกค้า checklist]
[  ] สร้าง SIP account แล้ว ทดสอบ login ผ่าน softphone ได้
[  ] อนุญาต register จาก Ingfah SIP Server IP
[  ] ตั้ง inbound route ของ DID ไปยัง extension นี้
```

:::note[ส่งข้อมูลกลับ]
ส่งฟอร์มที่กรอกครบแล้วทางอีเมลทีมงาน ingfah หรือช่องทางที่ตกลงไว้ ทีมงานจะดำเนินการตั้งค่าในระบบและติดต่อกลับเพื่อทดสอบการเชื่อมต่อร่วมกัน
:::
