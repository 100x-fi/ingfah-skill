# วิธีที่ 1: IP Peering

> วิธีเชื่อมต่อสำหรับลูกค้าที่มี SBC หรือ public static IP — ตั้งค่าด้วย IP whitelist ไม่มีการลงทะเบียน
>
> Source: https://docs.ingfah.ai/telephony/ip-peering/

## หลักการทำงาน

ทั้งสองฝั่งจะ "ไว้ใจ IP ของกันและกัน" สายขาเข้า/ขาออกส่งตรงระหว่าง IP ของลูกค้ากับ Ingfah SIP Server โดยไม่มีการลงทะเบียน (no REGISTER) ลูกค้าต้องเปิด firewall ให้ Ingfah SIP Server IP เข้ามาได้ และในทางกลับกัน Ingfah SIP Server ก็จะ whitelist IP ของลูกค้าไว้เช่นกัน

### สายเข้า (Inbound)

### สายออก (Outbound)

## ข้อมูลที่ต้องเตรียม

| ฟิลด์ | จำเป็น | คำอธิบาย | ตัวอย่าง / default |
|---|---|---|---|
| `name` | ✓ | ชื่อย่อใช้แทน trunk นี้ (ตัวอักษรอังกฤษ ไม่มีช่องว่าง) | `"abc-corp"` |
| `server` | ✓ | IP สาธารณะหรือ FQDN ของระบบ SIP ลูกค้า | `"27.254.205.133"` |
| `port` | — | SIP signaling port | default `5060` |
| `transport` | — | `"udp"` หรือ `"tls"` (ปลอดภัยกว่า ต้องใช้ cert) | default `"udp"` |
| `codec` | — | Array ของ codec ตามลำดับ: `["g722","ulaw"]` (HD + fallback, **แนะนำ**) หรือ `["ulaw"]` | default `["g722","ulaw"]` |
| `sip_user` | ✓ | SIP identity — user-part ของ SIP URI (`From:`, `Contact:`) | `"021088503"` |
| `number` | — | หมายเลข PSTN หรือ extension; routing key สำหรับโทรออก ถ้าต่างจาก `sip_user` ให้ระบุ | default = `sip_user` |
| `direction` | — | `"inbound"`, `"outbound"`, หรือ `"both"` | default `"both"` |

## สิ่งที่ลูกค้าต้องทำในระบบของตน

- เปิด firewall ให้รับ SIP/RTP จาก Ingfah SIP Server IP (ดู endpoint ที่ทีมงานส่งให้)
  - SIP: UDP 5060 หรือ TLS 5061
  - RTP: source port 10000–20000/udp *(ปลายทาง RTP ฝั่งท่านใช้ port range ของ PBX ตัวเอง — ไม่ต้องเปิด 10000–20000 ฝั่งตน)*
- กำหนดให้ระบบ route สายไปยัง Ingfah SIP Server endpoint ที่ทีมงานส่งให้
- หากใช้ **TLS**: ตรวจสอบ CN/SAN ของ cert ให้ตรงกับ hostname ที่ได้รับ
- ตกลง codec กับทีมงาน — **ฝั่ง ingfah แนะนำ `g722`** เพื่อคุณภาพ HD; ใช้ `ulaw` เฉพาะเมื่อฝั่งลูกค้าไม่รองรับ g722

## แบบฟอร์มเชื่อมต่อ

กรุณา copy ฟอร์มด้านล่าง กรอกข้อมูลให้ครบ แล้วส่งกลับให้ทีมงาน

```text
========== IP PEERING TRUNK ==========
ชื่อบริษัท/โครงการ  : ____________________
ผู้ติดต่อ           : ____________________
อีเมล / เบอร์โทร  : ____________________

[ข้อมูลทางเทคนิค]
name       : ____________________   (ชื่อย่อ ภาษาอังกฤษ)
server     : ____________________   (IP สาธารณะหรือ FQDN ของระบบท่าน)
port       : ____________________   (default 5060)
transport  : [  ] udp   [  ] tls
codec      : [  ] g722 (แนะนำ)  [  ] ulaw
sip_user   : ____________________   (SIP identity — ใช้ใน From: header)
number     : ____________________   (ระบุเฉพาะถ้าต่างจาก sip_user)

[ทิศทางการใช้งาน]
direction  : [  ] inbound   [  ] outbound   [  ] both (default)

[Firewall checklist]
[  ] อนุญาต SIP จาก Ingfah SIP Server IP (UDP 5060 หรือ TLS 5061)
[  ] อนุญาต RTP จาก Ingfah SIP Server IP source port 10000-20000/udp
[  ] route สายของหมายเลขไปยัง Ingfah SIP Server endpoint
```

:::note[ส่งข้อมูลกลับ]
ส่งฟอร์มที่กรอกครบแล้วทางอีเมลทีมงาน ingfah หรือช่องทางที่ตกลงไว้ ทีมงานจะดำเนินการตั้งค่าในระบบและติดต่อกลับเพื่อทดสอบการเชื่อมต่อร่วมกัน
:::
