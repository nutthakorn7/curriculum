# Worksheet 5 — Key Exchange: คนแอบกลางทาง (MITM) กับ Diffie-Hellman

> **Course:** Cryptography and Network Security (KOSEN69) · **{{ slot_label }}**
> **Kind:** Docker lab แบบทำตามทีละขั้น ไม่ต้องเขียนโปรแกรม และไม่ต้องคำนวณเลข

> **Ethics note:** ทำเฉพาะกับ container 3 ตัว (alice, bob, relay) ในเครื่องของตัวเองที่ lab นี้เปิดขึ้นมา ไม่มีพอร์ตเปิดออกนอกเครื่อง
> การแอบอยู่กลางทางของระบบที่ไม่ใช่ของเราและไม่ได้รับอนุญาตเป็นเรื่องผิดกฎหมาย

## อ่านก่อนเริ่ม

**วันนี้จะทำอะไร:** Alice กับ Bob อยากได้กุญแจลับร่วมกันผ่านเน็ตสาธารณะ จึงใช้ **Diffie-Hellman (DH)** แต่มี `relay` แอบอยู่กลางทาง เราจะดูสองรอบ: รอบ**ไม่ยืนยันตัวตน** relay อ่านข้อความของ Alice ได้โดยที่ทั้งสองคนไม่รู้ตัว และรอบ**ยืนยันด้วย HMAC** relay ล้มเหลว สิ่งที่ต้องจำ: **DH กันคนที่แค่แอบฟังได้ แต่ไม่กันคนที่แทรกกลางทาง**

**ทุกขั้นเขียนแบบเดียวกัน:**

| หัวข้อ | ความหมาย |
|---|---|
| **ทำอะไร** | บอกว่าขั้นนี้จะทำอะไร |
| **พิมพ์** | คัดลอกทั้งบรรทัดไปวางใน Terminal แล้วกด Enter |
| **ควรเห็น** | หน้าจอควรขึ้นประมาณนี้ |
| **แปลว่า** | ผลที่เห็นหมายความว่าอะไร |
| **ลงใบตอบ** | สิ่งที่ต้องคัดลอกหรือเขียนลงใบตอบ |

**คะแนน**

- ทุกคนทำ **Part A (60 คะแนน)** ซึ่งเหมือนกันทั้งสองแบบ
- จากนั้นทำ **เฉพาะแบบของตัวเอง (40 คะแนน)** ดูจากเลขตัวสุดท้ายของรหัสนักศึกษา: **เลขคี่ = Conventional (Part 2)**, **เลขคู่ = AIR-Sec (Parts 3–4)** (เลข 0 นับเป็นเลขคู่) แล้วเขียนแบบของตัวเองในช่อง Group
- ตอบเป็นภาษาไทยหรืออังกฤษก็ได้ ตอบสั้น ๆ ให้ชัดก็พอ
- **ใช้ใบตอบ:** ใน Classroom → Week 05 เปิดไฟล์ตามแบบของตัวเอง (`Wk05_Answer_Sheet_Conventional_odd_ID` หรือ `Wk05_Answer_Sheet_AIR-Sec_even_ID`) กด Open with → Google Docs พิมพ์ลงกรอบสีเทา แล้วกด File → Download → PDF
- ส่งไฟล์เดียว ตั้งชื่อตามรหัสนักศึกษา เช่น `Wk05_66990000.pdf` (ไม่ต้องใส่เครื่องหมาย `<` `>`) ที่ `learn.zcr.ai/submit` โดยใช้รหัสส่งงานของ Week 5 ที่ได้ทางอีเมล KMITL ภายใน **อาทิตย์ 6 ธ.ค. 23:59 น.**
- ข้อที่เขียนว่า *optional* ไม่มีคะแนน ไม่ต้องทำก็ได้

| Part A | คะแนน | ขั้นที่ลงใบตอบ |
|---|---:|---|
| A1 — relay แอบอ่านข้อความได้ | 20 | ขั้นที่ 2, 3 |
| A2 — ยืนยันกุญแจด้วย HMAC แล้ว relay ล้มเหลว | 20 | ขั้นที่ 6, 7, 8 |
| A3 — ทำไม HMAC หยุดได้ และข้อจำกัด | 20 | ขั้นที่ 10, 11, 12 |

**คำศัพท์ที่ต้องรู้**

| คำ | ความหมายแบบง่าย |
|---|---|
| Terminal / Docker / container | หน้าต่างพิมพ์คำสั่ง / โปรแกรมที่เปิด "เครื่องจำลอง" เล็ก ๆ ในเครื่องเรา ทำพังก็ลบแล้วเริ่มใหม่ได้ |
| Diffie-Hellman (DH) | วิธีให้สองฝ่ายได้ความลับร่วมกัน โดยส่งแค่ "ค่าสาธารณะ" ผ่านเน็ต คนที่แอบฟังเห็นแต่ค่าสาธารณะ คำนวณความลับไม่ได้ |
| ค่าสาธารณะ (public value) | ตัวเลขที่แต่ละฝ่ายส่งให้อีกฝ่ายเห็นได้ ไม่ใช่ความลับ |
| ความลับร่วม (shared secret) | ผลของ DH ใช้สร้างกุญแจเข้ารหัสข้อความ |
| relay / MITM | ตัวที่แอบอยู่กลางทาง ตอบรับ DH กับทั้งสองฝ่ายพร้อมกัน (man-in-the-middle) |
| HMAC / tag | "ตราประทับ" ที่คำนวณด้วยกุญแจลับ ใช้ตรวจว่าข้อมูลถูกแก้หรือไม่ (เรียนใน Week 3) |
| AUTH_KEY | กุญแจที่ Alice กับ Bob รู้ร่วมกันล่วงหน้า relay ไม่รู้ ใช้คำนวณ tag |
| log | ข้อความที่โปรแกรมพิมพ์เล่าว่ากำลังทำอะไร |

**คำถามที่มักสงสัย**

- *ต้องเก่งคณิตศาสตร์ไหม?* ไม่ต้อง วันนี้ไม่มีการคำนวณ
- *ต้องเขียนโปรแกรมไหม?* ไม่ต้อง คัดลอกคำสั่งไปวางได้เลย
- *ถ้าทำผิด เครื่องจะพังไหม?* ไม่พัง ทุกอย่างอยู่ใน container ถ้าสับสนให้พิมพ์ `docker compose -f docker-compose.vulnerable.yml down` และ `docker compose -f docker-compose.fixed.yml down` แล้วเริ่มใหม่
- *log ยาวและมีคำเตือน `CryptographyDeprecationWarning` เต็มไปหมด ผิดไหม?* ไม่ผิด เป็นคำเตือนว่า DH แบบนี้เก่าแล้ว ใบงานให้กรองเหลือเฉพาะบรรทัดที่ต้องดู
- *วางคำสั่งใน Terminal ยังไง?* คัดลอกคำสั่งจากใบงาน แล้ว Windows: กด Ctrl+V หรือคลิกขวา · Mac: กด Cmd+V จากนั้นกด Enter
- *คัดลอกผลจาก Terminal ยังไง?* ลากเมาส์คลุมข้อความก่อน แล้ว Windows: กด Ctrl+Shift+C · Mac: กด Cmd+C หรือจะ screenshot ก็ได้

**ถ้าเจอข้อความแบบนี้**

| ข้อความบนจอ | สาเหตุ | วิธีแก้ |
|---|---|---|
| มีคำว่า `Cannot connect to the Docker daemon` หรือ `error during connect` | ยังไม่ได้เปิด Docker | เปิด Docker Desktop รอจนขึ้น Engine running |
| `no configuration file provided: not found` หรือ `open docker-compose...: no such file` | Terminal ไม่ได้อยู่ในโฟลเดอร์ lab | ทำเตรียมขั้นที่ 4 อีกครั้ง |
| ขั้นที่ 2 หรือ 6 ขึ้นไม่ครบ | ยังรันไม่เสร็จ | รอ 10–15 วินาที แล้วพิมพ์คำสั่งเดิมอีกครั้ง |
| ขั้นที่ 6 มี `AUTH FAILED` แค่บรรทัดเดียว | อ่านจอเร็วเกินไป | รอสักครู่แล้วพิมพ์คำสั่งเดิมอีกครั้ง ต้องเห็นสองบรรทัด (alice และ bob) |
| Windows: `grep` ไม่รู้จัก | Windows ไม่มี `grep` | ใช้คำสั่งแบบ `findstr` หรือ PowerShell ที่ใบงานให้ไว้ในแต่ละขั้น |

ลองแล้วยังไม่ได้ ให้ถามเพื่อนหรืออาจารย์ได้เลย ถ้าใช้ Docker ไม่ได้จริง ๆ ให้บอกอาจารย์ แล้วตอบขั้นที่ 3 และ 10–12 จากการอ่านใบงานและรูป ขั้นที่เหลือเขียนกำกับว่า "ไม่ได้รันเอง"

---

## ก่อนเริ่ม: เตรียมเครื่อง (ทำที่บ้าน ทำครั้งเดียว)

ถ้าเคยทำ Week 2–4 มาแล้ว มี Docker และไฟล์ ZIP อยู่แล้ว เริ่มที่**เตรียมขั้นที่ 4** ได้เลย ถ้าหาโฟลเดอร์ `week05-key-exchanges` ไม่เจอ ให้โหลด ZIP ใหม่ตามเตรียมขั้นที่ 2

**ถ้าปิดเครื่องไปแล้วกลับมาทำต่อ:** ทำเตรียมขั้นที่ 1 และ 4 ใหม่

#### เตรียมขั้นที่ 1 — เปิด Docker Desktop

**ทำอะไร:** ถ้ายังไม่มี ให้ติดตั้งจาก <https://www.docker.com/products/docker-desktop/> แล้วเปิดโปรแกรมทิ้งไว้ **ควรเห็น:** ขึ้นว่า **Engine running**

#### เตรียมขั้นที่ 2 — โหลดและแตกไฟล์ lab

**ทำอะไร:** เปิด <https://github.com/nutthakorn7/security-cryptography> กดปุ่มสีเขียว **Code** แล้วเลือก **Download ZIP** (ไม่ต้องมีบัญชี GitHub) แล้วแตกไฟล์ (Windows: คลิกขวา **Extract All** · Mac: ดับเบิลคลิก) **ควรเห็น:** โฟลเดอร์ `security-cryptography-master` บางเครื่องมีโฟลเดอร์ชื่อเดียวกันซ้อนสองชั้น ให้เปิดเข้าไปจนเห็นโฟลเดอร์ `labs`

#### เตรียมขั้นที่ 3 — เข้าโฟลเดอร์ lab

**ทำอะไร:** เข้าไปที่ `labs` แล้วเข้า `week05-key-exchanges`

#### เตรียมขั้นที่ 4 — เปิด Terminal ในโฟลเดอร์ lab

- **Windows:** เปิดโฟลเดอร์ `week05-key-exchanges` ใน File Explorer คลิกขวาตรงที่ว่าง เลือก **Open in Terminal** (ถ้าไม่มี ให้กด Shift ค้างแล้วคลิกขวา เลือก **Open PowerShell window here**)
- **Mac:** เปิดแอป Terminal พิมพ์ `cd` เว้นวรรคหนึ่งครั้ง ลากโฟลเดอร์ `week05-key-exchanges` มาวางในหน้าต่าง แล้วกด Enter

เช็กว่าอยู่ถูกที่ด้วยคำสั่งนี้ (Windows ใช้ `dir`):

```bash
ls
```

**ควรเห็น:** มีชื่อ `docker-compose.vulnerable.yml` และ `docker-compose.fixed.yml` อยู่ในรายการ

#### เตรียมขั้นที่ 5 — สร้าง image (ต้องต่ออินเทอร์เน็ต)

**พิมพ์:**

```bash
docker compose -f docker-compose.vulnerable.yml build
```

**ควรเห็น:** ลงท้ายด้วย `Built` ครั้งแรกอาจรอหลายนาที ระหว่างนั้นอย่าปิดหน้าต่าง ถ้าทำเสร็จแล้ว ตอนเรียนจะเริ่มเร็วขึ้น

---

## Part A — The lab (both forms, 60 points)

Lab นี้มีสามตัวละคร: **Alice** ส่งข้อความลับหา **Bob** แต่ Alice ถูกตั้งให้ติดต่อผ่าน `relay` (ไม่ได้ต่อถึง Bob ตรง ๆ) นั่นคือสถานการณ์จริง: คนที่ "รับสายเมื่อเราโทรหา Bob" อาจไม่ใช่ Bob

![รูป: ในรอบไม่ยืนยันตัวตน Alice ทำ DH กับ relay ได้ความลับชุดหนึ่ง relay ทำ DH กับ Bob ได้ความลับอีกชุดหนึ่ง relay จึงถอดข้อความของ Alice อ่านแล้วเข้ารหัสส่งต่อให้ Bob ใหม่ Alice กับ Bob ไม่มีความลับร่วมกันโดยตรง (English: relay does one DH with Alice and another with Bob, so it can read and forward the message; Alice and Bob never share a secret with each other.)](img/w5-two-handshakes.svg)

### A1 — relay แอบอ่านข้อความได้ (20 points)

#### ขั้นที่ 1 — เปิดรอบ "ไม่ยืนยันตัวตน"

**ทำอะไร:** เปิด alice, bob และ relay ในรอบที่ไม่มีการยืนยันตัวตน แล้วรอให้ทำงานเสร็จ

**พิมพ์:**

```bash
docker compose -f docker-compose.vulnerable.yml up -d
```

**ควรเห็น:** มีคำว่า `Started` ประมาณสามบรรทัด รอประมาณ 15 วินาที ขั้นนี้ไม่ต้องลงใบตอบ

#### ขั้นที่ 2 — อ่าน log เฉพาะบรรทัดที่ต้องดู

**ทำอะไร:** ดู log และกรองเหลือเฉพาะบรรทัดของ ALICE, BOB และ RELAY

**พิมพ์** (Mac):

```bash
docker compose -f docker-compose.vulnerable.yml logs | grep -E "ALICE|BOB|RELAY"
```

**พิมพ์** (Windows PowerShell):

```powershell
docker compose -f docker-compose.vulnerable.yml logs | findstr "ALICE BOB RELAY"
```

**ควรเห็น:** ประมาณ 9 บรรทัด ให้หา**สี่บรรทัดนี้** (ลำดับอาจสลับเล็กน้อย ที่อยู่หลัง `from` เป็นเลขที่อยู่ในเครื่อง ไม่ต้องสนใจ)

```
RELAY: completed independent DH handshake with Alice (posing as Bob)
BOB RECEIVED: the launch code is 4471
RELAY: completed independent DH handshake with Bob (posing as Alice)
RELAY INTERCEPTED: the launch code is 4471
```

**แปลว่า:** relay ทำ DH แยกกันสองรอบ รอบแรกกับ Alice (แกล้งเป็น Bob) รอบที่สองกับ Bob (แกล้งเป็น Alice) แล้วถอดรหัสข้อความของ Alice อ่านได้ (`INTERCEPTED`) ขณะที่ Bob ก็ได้รับข้อความตามปกติ (`BOB RECEIVED`) ทั้งสองฝ่ายจึงไม่รู้ตัว ข้อความ `the launch code is 4471` เป็นข้อความตายตัวของ lab ไม่ใช่รหัสเฉพาะคน

**✍️ ลงใบตอบ (ขั้นที่ 2):** คัดลอกสี่บรรทัดข้างบนจากหน้าจอของตัวเอง

#### ขั้นที่ 3 — สรุปด้วยคำของตัวเอง

**ทำอะไร:** ดูรูปด้านบนแล้วเติมคำในช่องว่าง

> a) relay มีความลับร่วมกับ Alice **และ**มีความลับร่วมกับ Bob รวมเป็น ________ ชุด (1 / 2) ส่วน Alice กับ Bob (มี / ไม่มี) ความลับร่วมกันโดยตรง
>
> b) relay อ่านข้อความได้เพราะมัน (ได้ถอดรหัสด้วยความลับที่ตัวเองมี / ไปแก้สมการ DH ที่ยากมาก)

**✍️ ลงใบตอบ (ขั้นที่ 3):** เขียนทั้งสองประโยคให้ครบ

#### ขั้นที่ 4 — ปิดรอบแรก

**พิมพ์:**

```bash
docker compose -f docker-compose.vulnerable.yml down
```

**ควรเห็น:** ลงท้ายว่า `Removed` ขั้นนี้ไม่ต้องลงใบตอบ

### A2 — ยืนยันกุญแจด้วย HMAC แล้ว relay ล้มเหลว (20 points)

#### ขั้นที่ 5 — เปิดรอบ "ยืนยันด้วย HMAC"

**ทำอะไร:** รอบนี้ Alice กับ Bob แนบ tag (HMAC ด้วย AUTH_KEY) ไปกับค่าสาธารณะของตัวเอง relay ไม่รู้ AUTH_KEY

**พิมพ์:**

```bash
docker compose -f docker-compose.fixed.yml up -d
```

**ควรเห็น:** มีคำว่า `Started` รอประมาณ 15 วินาที ขั้นนี้ไม่ต้องลงใบตอบ

#### ขั้นที่ 6 — อ่าน log รอบที่สอง

**พิมพ์** (Mac):

```bash
docker compose -f docker-compose.fixed.yml logs | grep -E "ALICE|BOB|RELAY|AUTH"
```

**พิมพ์** (Windows PowerShell):

```powershell
docker compose -f docker-compose.fixed.yml logs | findstr "ALICE BOB RELAY AUTH"
```

**ควรเห็น:** ให้หา**สี่บรรทัดนี้** (relay ยังพยายามแทรกค่าของตัวเอง แต่ทั้ง alice และ bob ตรวจเจอและยกเลิก)

```
RELAY: (fixed mode) attempted DH substitution with Alice (posing as Bob)
RELAY: (fixed mode) attempted DH substitution with Bob (posing as Alice)
AUTH FAILED - ABORTING      (จาก bob)
AUTH FAILED - ABORTING      (จาก alice)
```

**แปลว่า:** relay ใช้โค้ดเกือบเดิมและยังแทรกค่าของตัวเอง แต่มันทำ tag ที่ถูกต้องให้ค่านั้นไม่ได้ เพราะไม่มี AUTH_KEY ทั้งสองฝ่ายจึงตรวจเจอและหยุด ก่อนจะส่งข้อความลับใด ๆ

**✍️ ลงใบตอบ (ขั้นที่ 6):** คัดลอกสี่บรรทัดข้างบน (ให้เห็นว่าบรรทัด `AUTH FAILED` มาจาก alice และ bob อย่างละหนึ่ง)

#### ขั้นที่ 7 — นับว่า relay อ่านข้อความได้กี่ครั้ง

**พิมพ์** (Mac):

```bash
docker compose -f docker-compose.fixed.yml logs | grep -c "RELAY INTERCEPTED"
```

**พิมพ์** (Windows PowerShell):

```powershell
(docker compose -f docker-compose.fixed.yml logs | Select-String -SimpleMatch "RELAY INTERCEPTED" | Measure-Object).Count
```

**ควรเห็น:** `0`

**แปลว่า:** ในรอบนี้ไม่มีบรรทัด `RELAY INTERCEPTED` เลย (ตัวเลขนี้บอกแค่ว่า relay ไม่ได้อ่านข้อความ ไม่ได้พิสูจน์ว่า Alice กับ Bob คุยกันสำเร็จ)

**✍️ ลงใบตอบ (ขั้นที่ 7):** เขียนตัวเลขที่ได้

#### ขั้นที่ 8 — สรุปด้วยคำของตัวเอง

**ทำอะไร:** เติมคำในช่องว่าง

> relay ทำ ________ ที่ถูกต้องให้ค่าสาธารณะของตัวเองไม่ได้ เพราะมันไม่มี ________ (เลือกคำ: `tag` / `AUTH_KEY`, ช่องที่สองตอบ `AUTH_KEY`)

**✍️ ลงใบตอบ (ขั้นที่ 8):** เขียนประโยคนี้ให้ครบ

#### ขั้นที่ 9 — ปิดรอบที่สอง

**พิมพ์:**

```bash
docker compose -f docker-compose.fixed.yml down
```

**ควรเห็น:** ลงท้ายว่า `Removed` ขั้นนี้ไม่ต้องลงใบตอบ

### A3 — ทำไม HMAC หยุดได้ และข้อจำกัด (20 points)

#### ขั้นที่ 10 — ดูโค้ดที่ทำ tag

**ทำอะไร:** อ่านสองบรรทัดนี้จาก `common.py` (ไม่ต้องพิมพ์อะไร) ฟังก์ชันแรกคำนวณ tag จากค่าสาธารณะและ AUTH_KEY ฟังก์ชันที่สองตรวจว่า tag ที่ได้รับตรงกับที่คำนวณเองหรือไม่

```python
return hmac.new(auth_key, pubkey_bytes, hashlib.sha256).digest()      # ทำ tag
return hmac.compare_digest(expected, tag)                            # ตรวจ tag
```

> tag ถูกคำนวณจาก ________ และ ________ (เลือกคำ: `ค่าสาธารณะ` / `AUTH_KEY` / `ข้อความลับ`)

**✍️ ลงใบตอบ (ขั้นที่ 10):** เขียนประโยคนี้ให้ครบ

#### ขั้นที่ 11 — ทำไมยังต้องทำ DH สดทุกครั้ง

**ทำอะไร:** อ่านแล้วตอบ 1–2 ประโยค Alice กับ Bob รู้ AUTH_KEY ร่วมกันอยู่แล้ว ทำไมไม่ใช้ AUTH_KEY เป็นกุญแจเข้ารหัสข้อความไปเลย (คำใบ้: ถ้าปีหน้า AUTH_KEY หลุด ข้อความที่มีคนบันทึกไว้เมื่อวันนี้จะเป็นอย่างไร ถ้ากุญแจแต่ละรอบสร้างจาก DH ใหม่ที่ลบความลับทิ้งแล้ว)

**✍️ ลงใบตอบ (ขั้นที่ 11):** เขียนคำตอบ

#### ขั้นที่ 12 — ข้อจำกัดของวิธีนี้

**ทำอะไร:** ตอบ 1–2 ประโยค วิธีนี้ใช้ได้เพราะเงื่อนไขหนึ่งข้อ คือ Alice กับ Bob ต้องมี AUTH_KEY ร่วมกัน**ล่วงหน้า**และเก็บเป็นความลับ ถ้า relay ได้ AUTH_KEY ไปด้วย จะเกิดอะไรขึ้น และ AUTH_KEY นี้ควรส่งให้กันผ่านทางไหน

**✍️ ลงใบตอบ (ขั้นที่ 12):** เขียนคำตอบ

#### ขั้นที่ 13 — เช็กก่อนไปต่อ

ดูว่าในใบตอบมีครบ: ขั้นที่ 2, 3 (A1), ขั้นที่ 6, 7, 8 (A2), ขั้นที่ 10, 11, 12 (A3) แล้วไปทำส่วนของแบบตัวเอง: เลขคี่ทำ Part 2 เลขคู่ทำ Part 3 และ Part 4

---

## Part 1 — Student Information
| Name | Student ID | Date | Group (your form) | AI tools used (which, for what) |
|---|---|---|---|---|
| | | | | |

---

## Part 2 — Conventional form (40 points; only if Conventional is your assigned form)

ตอบข้อละ 2–3 ประโยค ภาษาไทยได้ ส่วนนี้ให้**ตอบด้วยตัวเอง** ไม่ใช้ AI ตอบ ไม่ต้องคำนวณ

**Q1 (10). ทำไมไม่ส่งกุญแจ AES ตรง ๆ ผ่านเน็ต.** ถ้าส่งกุญแจไปตรง ๆ คนที่แอบฟังจะได้อะไร และ DH ให้ Alice กับ Bob ทำอะไรได้แทน (คำใบ้: ค่าสาธารณะ)

**Q2 (10). relay อ่านได้อย่างไร.** ในรอบไม่ยืนยันตัวตน ใครมีความลับร่วมกับ Alice และใครมีกับ Bob relay อ่านข้อความได้อย่างไรโดยไม่ต้องแก้ปัญหายาก ๆ (คำใบ้: ขั้นที่ 2 และ 3)

**Q3 (10). HMAC หยุดอะไร.** DH ธรรมดากันคนที่แค่แอบฟังได้ แต่ relay แทรกค่าของตัวเองได้ HMAC ในรอบที่สองหยุดอะไร และวิธีนี้ต้องมีเงื่อนไขอะไรข้อหนึ่ง (คำใบ้: ขั้นที่ 6 และ 12)

**Q4 (10). ทำไมยังทำ DH สด.** ทำไมรอบที่สองยังสร้างกุญแจใหม่ด้วย DH แทนที่จะใช้ AUTH_KEY เข้ารหัสข้อความ ถ้า AUTH_KEY หลุดทีหลัง ข้อความที่บันทึกไว้ก่อนหน้าจะเป็นอย่างไร (คำใบ้: ขั้นที่ 11)

### Going further (optional — no marks)

- Why use a large, well-known DH group (RFC 3526)? What if a peer's public value is not validated?
- How do ECDH and X25519 differ from this finite-field demo?
- Authenticated DH needs a trusted way to share the key or certificate first. What is that "trust bootstrap" in TLS?

---

## Part 3 — AIR-Sec Arm: Audit the AI (AIR-Sec version only, 20 points)

AI is a power tool you must **distrust** — you are graded on your *critique*, not the AI's answer.

เพื่อนคนหนึ่งถาม AI ว่าจะกันคนแทรกกลางใน DH ได้อย่างไร AI ตอบ (ภาษาอังกฤษ ไม่ต้องแปลทุกคำ):

> **AI's answer:**
> "Alice and Bob can run plain DH, derive a fresh session key, and then authenticate every message with HMAC under that derived key. A MITM cannot know the session key, so a valid message HMAC proves Bob's identity. No certificate or pre-shared key is needed."
>
> — end of AI answer —

ทำตามนี้ (ใช้สิ่งที่เห็นในแล็บ):

1. **Find what's wrong.** คัดลอกประโยคที่ผิด แล้วเขียน 1–2 ประโยคว่าทำไมผิด (คำใบ้: ในขั้นที่ 2 relay ก็มี "กุญแจ session" ของตัวเองกับ Alice อยู่แล้ว)
2. **Write the corrected version.** เขียนคำอธิบายที่ถูกต้อง 2–3 ประโยค โดยบอกว่าต้องมีอะไรที่ relay ไม่มี (คำใบ้: ขั้นที่ 6 และ 12)

> Disclose any other AI use in the Part 1 table. This task counts toward the **Audit the AI** row.

---

## Part 4 — Comprehension & Prompt (AIR-Sec version only: EiPE 10 + Prompt 10)

**A. Explain in Plain English (EiPE, 10).** อธิบายให้เพื่อนที่ไม่เคยเรียน DH ฟัง 2–4 ประโยค **ไม่ใช้ศัพท์ยาก** ว่าในรอบแรก ใครมีความลับร่วมกับ Alice ใครมีกับ Bob และทำไม relay จึงอ่านและส่งต่อข้อความได้ (คำใบ้: ดูรูปและขั้นที่ 3 แล้วใช้คำพูดของตัวเอง)

**B. Prompt Problem (10).** ใช้ AI ตัวไหนก็ได้ แล้วทำตามนี้:

1. เขียน prompt **หนึ่งอัน** เช่น *"Explain why authenticated Diffie-Hellman prevents a man-in-the-middle attack"*
2. คัดลอกคำตอบของ AI ลงใบตอบ
3. ตรวจคำตอบของ AI ทีละข้อ แล้วติ๊ก **ผ่าน / ไม่ผ่าน** พร้อมเหตุผลสั้น ๆ 1 ประโยคต่อข้อ:

- AI แยก "กันคนแอบฟัง" (DH ธรรมดามีให้แล้ว) ออกจาก "ยืนยันว่าอีกฝั่งคือใคร" (DH ธรรมดาไม่มี) หรือไม่
- AI บอกไหมว่าต้องผูกค่าสาธารณะกับตัวตนอย่างไร (เช่น tag, ลายเซ็น, ใบรับรอง) และกุญแจหรือใบรับรองนั้นต้องถูกส่งให้ถึงกันอย่างปลอดภัยก่อน
- AI แต่งเรื่องหรือพูดผิดไหม (Does it make anything up?) เช่น ตั้งชื่อวิธีที่ไม่มีจริง

ส่ง **prompt + คำตอบของ AI + ตารางตรวจพร้อมเหตุผลของตัวเอง**

---

## 🎤 Viva spot-check (formative/authenticity check; no separate points)

An instructor may ask any of these live, at random, to confirm you did the work yourself:

1. "ในขั้นที่ 2 relay ทำ DH สองรอบก่อนพิมพ์ `RELAY INTERCEPTED` ทำไมต้องสองรอบ ถ้าทำแค่รอบเดียวจะเป็นอย่างไร"
2. "ในขั้นที่ 6 relay ยังแทรกค่าของตัวเอง ใช้โค้ดเกือบเดิม ทำไมคราวนี้ล้มเหลว"
3. "Alice กับ Bob มี AUTH_KEY ร่วมกันอยู่แล้ว ทำไมไม่ใช้เป็นกุญแจเข้ารหัสเลย (ขั้นที่ 11)"

---

## Grading rubric — assigned version totals 100

| Criterion | Conventional | AIR-Sec |
|---|---:|---:|
| A1 — relay reads the message | 20 | 20 |
| A2 — HMAC check stops relay | 20 | 20 |
| A3 — why it works + limits | 20 | 20 |
| Conventional written questions (Q1–Q4) | 40 | — |
| AIR-Sec Audit the AI | — | 20 |
| AIR-Sec Explain in Plain English (EiPE) | — | 10 |
| AIR-Sec Prompt Problem | — | 10 |
| **Total for the assigned version** | **100** | **100** |

## Evidence & Integrity (required)

- ใส่ชื่อ รหัสนักศึกษา และวันที่ในใบตอบ และคัดลอกคำสั่งกับผลจากเครื่อง**ของตัวเอง** บรรทัด `the launch code is 4471` เป็นข้อความตายตัวของ lab เหมือนกันทุกคน ไม่ใช่ flag เฉพาะคน ห้ามเอาผลของเพื่อนมาส่งเป็นของตัวเอง
- **อธิบายด้วยคำของตัวเอง** (ให้คะแนนจากเหตุผล): ข้อที่ให้เติมคำ (ขั้นที่ 3, 8, 10) ใช้คำที่ให้ไว้ได้เลย ส่วนคำตอบสั้น ๆ ของขั้นที่ 11 และ 12 และข้อเขียนของฟอร์มตัวเองต้องเขียนด้วยคำของตัวเอง

**กำหนดส่งและการส่งช้า:** ส่งภายใน 23:59 น. (เวลาไทย) ของ **อาทิตย์ 6 ธ.ค.** ส่งช้าหักวันละ 10% ของคะแนนใบงานนี้ (ไม่เต็มวันนับเป็นหนึ่งวัน) จนเหลือ 0 การอัปโหลดหรือเปลี่ยนไฟล์หลังกำหนดส่งนับว่าส่งช้าทั้งชิ้น ส่งงานร่วม 60 คะแนน และแบบของตัวเอง**หนึ่งแบบ**เท่านั้น ทำทั้งสองแบบไม่ได้คะแนนเพิ่ม Viva ใช้ตรวจความเข้าใจ ไม่มีคะแนนแยก
