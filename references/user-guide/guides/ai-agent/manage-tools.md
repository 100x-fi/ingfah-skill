# สร้างและจัดการ Tools

> สร้าง Tool ให้ AI Agent เรียกระบบภายนอกระหว่างสนทนา ทดสอบได้ และเขียนโค้ด JavaScript หรือ Python ได้
>
> Source: https://docs.ingfah.ai/guides/ai-agent/manage-tools/

หน้า **Tools** ใช้สร้างและจัดการ Tool ที่ AI Agent เรียกใช้ระหว่างสนทนา เช่น ดึงยอดค้างชำระจากระบบหลังบ้าน หรือบันทึกนัดหมายกลับเข้าระบบของคุณ

หน้านี้ใช้ **สร้าง Tool** ส่วนวิธีนำ Tool ไปผูกกับ AI Agent ดูที่ [การใช้ Tools ใน AI Agent](/guides/ai-agent/ai-agent-tools/)

งานบนสายโทรศัพท์ เช่น Goal Form หรือโอนสาย ก็อยู่หมวด **Phone Tools** ดูที่ [Phone Tools](/guides/ai-agent/phone-tools/)

## เหมาะกับงานแบบไหน

| แบบ Integration | ใช้เมื่อ |
|-----------------|----------|
| **http** | ระบบของคุณมี API พร้อมแล้ว และอยากให้ Agent เรียก URL ตรง ๆ ด้วยพารามิเตอร์จากบทสนทนา |
| **wasm** (เขียนโค้ด) | ต้องคำนวณ แปลงค่า หรือเรียกหลายขั้นก่อนตอบ Agent หรืออยากควบคุม logic เองด้วย JavaScript / Python |

ตัวอย่างงานที่ใช้บ่อย

- เช็คสถานะออเดอร์จาก ERP แล้วให้อ่านสถานะกับลูกค้า
- คำนวณยอดหรือสิทธิ์ตามกฎธุรกิจที่ซับซ้อนเกินกว่าสูตรสั้น ๆ
- เก็บเลขสัญญาจากลูกค้าแล้ว ค่อยเปิดเคสใน CRM

## รายการ Tools

| คอลัมน์ | ความหมาย |
|---------|----------|
| Signature | ชื่อทางเทคนิคที่ AI Agent ใช้เรียก Tool |
| ประเภท Integration | ระบบปลายทางที่ Tool นี้เชื่อมต่อ |
| Method | รูปแบบการเรียกใช้งาน |
| คำอธิบายสำหรับ AI Agent | คำอธิบายที่ AI ใช้ตัดสินใจว่าจะเรียก Tool นี้เมื่อไหร่ |
| แก้ไขล่าสุด | วันที่แก้ไขล่าสุด |

กรองตามประเภท Tool (**ของระบบ** หรือ **สร้างเอง**) ตาม Integration และตาม Method ได้ ค้นจาก signature พารามิเตอร์ หรือคำอธิบายก็ได้

## สร้าง Tool ใหม่

กด **สร้าง Tool** แล้วกรอกข้อมูล

### ข้อมูลหลัก

| ช่อง | รายละเอียด |
|------|-----------|
| **Signature** | ชื่อฟังก์ชันที่ AI เรียกใช้ ใช้ได้เฉพาะ a-z, A-Z, 0-9 และ `_` และห้ามซ้ำกับ Tool อื่น |
| **ชื่อ** | ชื่อที่ใช้แสดงในระบบ |
| **คำอธิบายสำหรับ AI Agent** | อธิบายว่า Tool นี้ทำอะไรและควรใช้เมื่อไหร่ |

:::tip[ตั้งชื่อ Signature ให้ตรงหน้าที่]
ตั้งชื่อ signature ให้ตรงหน้าที่ เช่น `get_outstanding_balance` AI Agent ก็จะเรียก Tool ได้แม่นยำขึ้น
:::

### Function Parameters

คือค่าที่ **AI Agent จะใส่ให้เอง** ตอนคุยกับลูกค้า เช่น เลขที่สัญญาที่ลูกค้าเพิ่งแจ้งมา

แต่ละพารามิเตอร์ประกอบด้วย

- **ชื่อพารามิเตอร์** ต้องขึ้นต้นด้วยตัวอักษร ใช้ a-z, A-Z, 0-9 และ `_` และห้ามซ้ำ
- **คำอธิบาย** บอก AI ว่าค่านี้คืออะไร
- **ประเภท** String, Number, Boolean, Object หรือ Array
- **จำเป็น** ระบุว่าต้องมีค่านี้เสมอหรือไม่

### Integration Parameters

คือค่าที่ **คุณกำหนดไว้ล่วงหน้า** เพื่อเชื่อมระบบปลายทาง เช่น URL หรือ Token เลือก **ประเภท Integration** กับ **Method** แล้วกรอกคู่ Key/Value

ค่าที่เป็นความลับ ระบบจะซ่อนเป็นจุดไข่ปลาเสมอ

ถ้าต้องใช้ค่าซ้ำในหลาย Tool ก็ให้เก็บไว้ที่ [Secrets](/guides/settings/secrets/) แล้วอ้างอิงด้วย `{{ secrets.NAME }}` ในช่องที่เป็น http หรือ wasm

### เขียน Tool ด้วยโค้ด (JavaScript / Python)

พอเลือก Integration แบบ **wasm** ก็เขียนโค้ดเองได้สองภาษา

| ช่อง | รายละเอียด |
|------|-----------|
| **ภาษา** | JavaScript หรือ Python |
| **โค้ด** | ฟังก์ชัน `run` ที่รับ `args`, `secrets` และ `http` **ไม่รองรับการ import package** และโค้ดยาวได้ไม่เกิน 1 MiB |

ระบบมีโค้ดตัวอย่างตอนเลือก wasm หรือตอนเปลี่ยนภาษา พอเปลี่ยนภาษา ระบบก็จะแทนที่โค้ดบนหน้าจอด้วยตัวอย่างของภาษานั้นทันที ย้อนกลับไม่ได้

อ่าน Secret ในโค้ดได้ผ่าน `secrets` เช่น `secrets.CRM_API_KEY` (ต้องมี Secret ชื่อนี้อยู่แล้ว) เรียก HTTP ออกไปก็ใช้ `http.get` หรือเมธอดอื่นที่ระบบเตรียมไว้

กฎสำคัญของโค้ด

- ต้องมีฟังก์ชัน `run` และ **คืนค่าเป็น object** เสมอ
- ออกเน็ตได้แค่ผ่าน `http` ไม่มี `fetch` หรือ `import requests`
- JavaScript ห้าม import package ส่วน Python ใช้ได้เฉพาะไลบรารีมาตรฐานบางตัว
- รันได้ไม่เกิน **10 วินาที** รวมการเรียก HTTP

:::note[Tool จากไฟล์ .wasm]
ถ้าสร้าง Tool จากไฟล์ `.wasm` หน้าจอก็จะไม่มีโค้ดให้ดู กดแก้ไขแล้วเขียนโค้ดใหม่แทนได้
:::

### ตัวอย่างโค้ด เช็คสถานะลูกค้า

1. สร้าง Secret ชื่อ `CRM_API_KEY` ที่ [Secrets](/guides/settings/secrets/)
2. กด **สร้าง Tool** ตั้ง Signature เช่น `check_customer`
3. ใส่ Function Parameter ชื่อ `customer_id` ประเภท String และติ๊กจำเป็น
4. เลือก Integration **wasm** ภาษา **JavaScript** แล้ววางโค้ด

```js
export default async function run({ args, secrets, http }) {
  const res = http.get("https://api.example.com/customers", {
    query: { id: args.customer_id },
    headers: { Authorization: `Bearer ${secrets.CRM_API_KEY}` },
  });
  if (!res.ok) throw new Error(`CRM answered ${res.status}`);
  const data = res.json();
  return {
    customer_id: data.id,
    status_th: data.status_th,
    say: `สถานะของลูกค้าคือ ${data.status_th}`,
  };
}
```

Python รูปเดียวกัน

```python
def run(args, secrets, http):
    res = http.get(
        "https://api.example.com/customers",
        query={"id": args["customer_id"]},
        headers={"Authorization": f"Bearer {secrets['CRM_API_KEY']}"},
    )
    if not res.ok:
        raise Exception(f"CRM answered {res.status}")
    data = res.json()
    return {
        "customer_id": data["id"],
        "status_th": data["status_th"],
        "say": f"สถานะของลูกค้าคือ {data['status_th']}",
    }
```

5. กด **ทดสอบโค้ด** ด้วยค่า เช่น `customer_id = C-1029`
6. บันทึก แล้วไปเปิด Tool นี้บน AI Agent ตาม [การใช้ Tools ใน AI Agent](/guides/ai-agent/ai-agent-tools/)
7. ใน Flow เขียนชัดว่า พอลูกค้าบอกเลขลูกค้าแล้ว ก็ให้เรียก `check_customer` แล้วอ่านค่า `say` กลับ

:::tip[ตัวอย่างการสั่ง Skill]
ช่วยสร้าง Tool แบบ wasm ชื่อ check_customer ให้ Agent "มะลิ" รับ customer_id แล้วเรียก https://api.example.com/customers ด้วย Secret CRM_API_KEY คืนข้อความภาษาไทยที่ Agent อ่านให้ลูกค้าได้
:::

สร้างผ่าน API Key ได้ด้วย ใช้สิทธิ์ `ai_agents:write`

เอกสารอยู่ที่ [developers.ingfah.ai](https://developers.ingfah.ai) หัวข้อ Code tools และ Plugin functions

## ทดสอบการใช้งาน

ที่หน้ารายละเอียด Tool มีสองแบบตามประเภท Integration

- **ทดสอบการใช้งาน** สำหรับ Tool ที่เรียกปลายทางภายนอก ใส่ค่าพารามิเตอร์แล้วกด **ทดสอบ**
- **ทดสอบโค้ด** สำหรับ Tool แบบ wasm ทดสอบโค้ดเวอร์ชันที่อยู่บนหน้าจอ ระบบจะ build แล้วรันให้ ทดสอบได้ไม่เกิน 10 ครั้งต่อนาที

:::danger[การทดสอบเป็นการเรียกใช้งานจริง]
ระบบจะเรียกปลายทางจริง หรือรันโค้ดจริง ไม่ใช่การจำลอง (Dry Run) ถ้า Tool นี้สร้างหรือเปลี่ยนข้อมูลในระบบของคุณ การกดทดสอบก็จะเกิดผลจริง
:::

ถ้า build ไม่ผ่าน ระบบก็จะแจ้งข้อความผิดพลาดพร้อมบรรทัดที่เกี่ยวข้อง และยังบันทึกไม่ได้จนกว่าจะแก้โค้ด

## แก้ไข ทำสำเนา และลบ

- **แก้ไข** แก้ได้เฉพาะ Tool ที่สร้างเอง
- **ทำสำเนา** คัดลอกเนื้อหาและพารามิเตอร์ทั้งหมด **แต่ไม่รวมการเชื่อมต่อกับ AI Agents** และต้องตั้ง signature ใหม่ที่ไม่ซ้ำ
- **ลบ** ลบแล้วกู้คืนไม่ได้ ถ้ายังมี AI Agent ใช้ Tool นี้อยู่ ระบบก็จะไม่ยอมให้ลบ และจะแสดงรายชื่อ Agent ที่ใช้อยู่

:::caution[การแก้ไขกระทบ Agent ที่ใช้อยู่]
การแก้ Tool อาจกระทบ AI Agent ที่กำลังใช้อยู่ ก่อนแก้ทุกครั้ง ให้ดูรายชื่อที่หัวข้อ **AI Agent ที่ใช้งาน** ในหน้ารายละเอียด Tool
:::
