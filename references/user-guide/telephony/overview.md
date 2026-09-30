# ภาพรวม — เลือกวิธีเชื่อมต่อ

> เปรียบเทียบ IP Peering กับ SIP Registration และการตั้งค่าทิศทาง inbound/outbound
>
> Source: https://docs.ingfah.ai/telephony/overview/

เอกสารชุดนี้สำหรับลูกค้าที่ต้องการเชื่อมต่อระบบโทรศัพท์ (PBX / SBC / SIP Trunk) เข้ากับแพลตฟอร์ม **Ingfah** เพื่อรับ-ส่งสายผ่านระบบ Ingfah SIP Server

:::note[Endpoint ฝั่ง ingfah]
Hostname / FQDN, IP Address และ Port จะส่งให้แยกต่างหากโดยทีมงาน
:::

## เลือกวิธีเชื่อมต่อ

ระบบ ingfah รองรับการเชื่อมต่อ SIP ได้ 2 รูปแบบหลัก:

| วิธี | เหมาะกับ | การยืนยันตัวตน | ทิศทางการเชื่อม |
|---|---|---|---|
| **IP Peering** | ลูกค้าที่มี SBC / public static IP เช่น Carrier, NT, ITSP, MS Teams Direct Routing | IP-based (ไม่มี username/password) | ทั้งสองฝั่งส่งสายหากันโดยตรงผ่าน IP |
| **SIP Registration** | ลูกค้าที่ใช้ PBX ทั่วไป (3CX, Yeastar, FreePBX, Cloud PBX) ที่ไม่มี public static IP | username + password | Ingfah SIP Server ไปลงทะเบียนเป็น client กับ SIP server ของลูกค้า |

:::tip[ไม่แน่ใจว่าจะเลือกแบบไหน?]
- ถ้าฝั่งลูกค้าสามารถบอก IP ที่แน่นอนได้ และพร้อมเปิด firewall → ใช้ **IP Peering**
- ถ้ามีเฉพาะ SIP username / password และ server hostname → ใช้ **SIP Registration**
:::

## ทิศทางการเชื่อมต่อ: inbound vs outbound

ทั้งสองวิธีรองรับสายทั้ง **เข้า (inbound)** และ **ออก (outbound)** แต่กลไกต่างกัน

**outbound-only** พบเมื่อ AI agent ต้องการโทรหาลูกค้าแต่ไม่รับสายเข้า **inbound-only** คือทรังก์สำหรับรับ hotline เข้าเท่านั้น ทั้งสองกรณีให้ระบุฟิลด์ `direction` ในแบบฟอร์มให้ชัดเจน เพื่อป้องกัน route ผิดทิศและค่าโทรที่ไม่คาดคิด

### เปรียบเทียบเชิงเทคนิค

| ประเด็น | IP Peering | SIP Registration |
|---|---|---|
| Persistent connection | ❌ ไม่มี — call ต่อ call | ✅ มี REGISTER session ตลอด |
| Firewall ฝั่งลูกค้า | ต้องเปิด 2 ทิศ (in + out) | ไม่ต้องเปิดอะไรเพิ่ม |
| การยืนยันตัวตน | IP whitelist 2 ฝั่ง | username + password |
| ใครเริ่ม contact | ใครก็ได้ที่มีสาย | Ingfah SIP Server เป็นฝ่าย REGISTER ก่อนเสมอ |
| รองรับ dynamic IP ฝั่งลูกค้า | ❌ ต้องใช้ public static IP | ✅ ได้ |
| กำหนดทิศทางได้ | ✅ inbound / outbound / both | ✅ inbound / outbound / both |
