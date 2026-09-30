// One entry = one finished call and the outcome it should get. Build these
// from real calls (GET /client/chat-sessions/{uuid}), with names, phone
// numbers, ID numbers and addresses replaced by placeholders before they are
// saved here. Include the borderline calls: they are the ones worth testing.
// The examples below match example/product.json.

const call = (id, expectedOutcome, lines) => ({
  description: `[${id}] expects ${expectedOutcome}`,
  vars: { expectedOutcome, transcript: lines.join('\n') },
});

module.exports = [
  call('confirmed', 'ยืนยันออเดอร์', [
    'agent: สวัสดีค่ะ คุณลูกค้า มะลิจากร้านขนมตัวอย่างนะคะ โทรมายืนยันออเดอร์ที่สั่งไว้ สะดวกคุยสักครู่ไหมคะ',
    'user: ได้ค่ะ',
    'agent: ขอทวนออเดอร์นะคะ มีขนมชั้น 2 กล่อง ยอดรวม 360 บาท จัดส่งพรุ่งนี้ช่วงบ่าย ถูกต้องไหมคะ',
    'user: ถูกต้องค่ะ',
    'agent: ขอบคุณมากค่ะ ขอให้เป็นวันที่ดีนะคะ สวัสดีค่ะ 😊',
  ]),
  call('changed', 'แก้ไขออเดอร์', [
    'agent: ขอทวนออเดอร์นะคะ มีขนมชั้น 2 กล่อง ยอดรวม 360 บาท จัดส่งพรุ่งนี้ช่วงบ่าย ถูกต้องไหมคะ',
    'user: ขอเปลี่ยนเป็นสามกล่องได้ไหมคะ',
    'agent: ได้ค่ะ เดี๋ยวแจ้งร้านเปลี่ยนเป็นสามกล่องให้นะคะ',
  ]),
  // Borderline: busy, but says "yes" to the greeting first.
  call('busy-after-yes', 'โทรกลับภายหลัง', [
    'agent: สะดวกคุยสักครู่ไหมคะ',
    'user: ค่ะ... อ๊ะ ขอโทษค่ะ ตอนนี้ขับรถอยู่ ไว้โทรมาใหม่นะคะ',
    'agent: ไม่เป็นไรค่ะ เดี๋ยวมะลิโทรกลับอีกครั้งนะคะ ขออนุญาตวางสายค่ะ',
  ]),
  call('dropped', 'สรุปไม่ได้', [
    'agent: สวัสดีค่ะ คุณลูกค้า มะลิจากร้านขนมตัวอย่างนะคะ',
    'user: ฮัลโหล',
  ]),
];
