# Thailand Macro Dashboard: ค่าเงินบาท · เงินเฟ้อ · ดอกเบี้ยนโยบาย

> ⚠️ **คำเตือน / Disclaimer**
> โปรเจกต์นี้ทำขึ้น **เพื่อการศึกษาเท่านั้น** ไม่ได้ใช้ในเชิงพาณิชย์ ไม่ใช่คำแนะนำการลงทุน
> และไม่ได้มีเจตนาทำให้บุคคลหรือองค์กรใดเสียหาย ข้อมูลเป็นของธนาคารแห่งประเทศไทย (ธปท.)
> และ BIS ตามที่ระบุในตารางด้านล่าง โปรดตรวจสอบตัวเลขกับแหล่งข้อมูลทางการก่อนนำไปใช้ทุกครั้ง
>
> *For educational purposes only. Not for commercial use, not investment advice, and not
> intended to harm any person or organization. Data belongs to the Bank of Thailand and the BIS,
> as listed below.*

ดึงข้อมูลเศรษฐกิจไทยจาก BOT API และ BIS ด้วย Python แล้วเขียนเป็นไฟล์ JSON ไฟล์เดียว ให้หน้าเว็บนำไปแสดง

หน้าเว็บเขียนด้วย React + TypeScript หน้าตาแบบแอป iOS เน้นการเปิดบนมือถือ มีภาษาไทยและอังกฤษ และเปลี่ยนเป็น dark mode ตามเครื่อง GitHub Actions สร้างข้อมูลและเผยแพร่บน GitHub Pages ทุกวัน

## ข้อมูลที่ดึง

ตัวชี้วัดทั้งหมดอยู่ใน `src/series.py` ไฟล์เดียว ตัวละหนึ่งรายการ

| id | ข้อมูล | แหล่ง | ความถี่ | ถือว่าเก่าเกินเมื่อ |
|---|---|---|---|---|
| `usd_thb` | อัตราแลกเปลี่ยน USD/THB (อัตรากลาง เฉลี่ยรายวัน) | [BOT API](https://portal.api.bot.or.th) Exchange Rates | รายวัน | เกิน 7 วัน |
| `policy_rate` | ดอกเบี้ยนโยบาย และวันประชุม กนง. ล่าสุด | อัตรา: [BIS Data Portal](https://data.bis.org) `WS_CBPOL` จากข้อมูลของ ธปท. วันประชุม: BOT API Policy Rate | ตามมติ กนง. | ไม่ตรวจ |
| `cpi_yoy` | เงินเฟ้อทั่วไป YoY | [BIS Data Portal](https://data.bis.org) `WS_LONG_CPI` | รายเดือน | เกิน 120 วัน |

BIS ไม่ต้องใช้ key และอนุญาตให้นำข้อมูลไปเผยแพร่ต่อเพื่อการที่ไม่ใช่เชิงพาณิชย์ หน้าเว็บระบุแหล่งที่มาไว้ที่ตัวชี้วัดแต่ละตัว

BOT API ใช้ token แยกตามแอปใน portal และแต่ละแอป subscribe หมวดเดียว ค่าเงินใช้แอปที่ subscribe หมวด Exchange Rates โค้ดอ่าน token จากตัวแปร `BOT_TOKEN_EXCHANGE` วันประชุม กนง. ใช้แอปที่ subscribe หมวด Policy Rate อ่านจาก `BOT_TOKEN_POLICY`

กราฟดอกเบี้ยนโยบายยังใช้ BIS เพราะ BOT API รุ่นปัจจุบัน (`/PolicyRate/v3`) ให้แค่ค่าล่าสุด ไม่มีประวัติย้อนหลัง แต่ให้วันประกาศมติครั้งล่าสุด ซึ่งบอกวันประชุมได้แม้มตินั้นจะคงอัตราไว้ และ BOT ไม่มีเงินเฟ้อทั่วไปของทั้งประเทศ CPI จึงใช้ BIS เช่นกัน

เพิ่มตัวชี้วัดใหม่ได้โดยเพิ่ม `Series` หนึ่งรายการใน `SERIES` พร้อมฟังก์ชันดึงข้อมูลที่คืนคอลัมน์ `date` และ `value`

## วิธีใช้

```bash
pip install -r requirements-dev.txt
python src/build_data.py --sample   # ข้อมูลตัวอย่าง ไม่ต้องมี token
pytest -q tests
```

`python src/build_data.py` ดึงข้อมูลจริงจากแหล่งข้างบน ต้องตั้งตัวแปร `BOT_TOKEN_EXCHANGE` และ `BOT_TOKEN_POLICY` ก่อน

ไฟล์จะออกที่ `web/public/data/dashboard.json` เปลี่ยนที่ได้ด้วย `--out`

ถ้าแหล่งใดตอบ error หรือข้อมูลล่าสุดเก่ากว่าที่กำหนดในตารางข้างบน สคริปต์จะหยุดพร้อมบอกสาเหตุ และไม่เขียนไฟล์ ข้อมูลตัวอย่าง **ไม่ใช่ตัวเลขจริงของ ธปท.** และไฟล์จะมี `"source": "sample"` กำกับไว้

## หน้าเว็บ

```bash
python src/build_data.py --sample   # สร้าง web/public/data/dashboard.json
cd web
npm install
npm run dev     # เปิด http://localhost:5173
npm test        # vitest
npm run build   # typecheck แล้ว build ลง web/dist
```

| ไฟล์ | หน้าที่ |
|---|---|
| `web/src/data.ts` | type ของ `dashboard.json` และตัวตรวจรูปแบบตอนโหลด |
| `web/src/derive.ts` | คำนวณค่าล่าสุด การเปลี่ยนแปลง ช่วงเวลา และพิกัดกราฟ |
| `web/src/components/Overview.tsx` | หน้ารวม แบ่งหมวดพร้อมกราฟเล็ก |
| `web/src/components/Detail.tsx` | หน้ารายละเอียด กราฟใหญ่ เลือก 6M / 1Y / 3Y |
| `web/src/i18n.ts` | ข้อความภาษาไทยและอังกฤษ |

หน้ารายละเอียดใช้ hash ใน URL เช่น `#usd_thb` จึงกดปุ่มย้อนกลับของเบราว์เซอร์และแชร์ลิงก์ได้

## GitHub Actions

`.github/workflows/update.yml` รัน test ของ Python และหน้าเว็บทุก push และ pull request ทุกวันเวลาประมาณ 18:00 น. ตามเวลาไทย (GitHub มักเริ่มช้ากว่านั้น) จะดึงข้อมูลจริง build หน้าเว็บ แล้วเผยแพร่ขึ้น GitHub Pages

ต้องเปิด GitHub Pages ก่อนครั้งแรก ที่ **Settings → Pages → Source** ให้เลือก **GitHub Actions**

ขั้นดึงข้อมูลจริงใช้ repository secret ที่ **Settings → Secrets and variables → Actions**

| Secret | หมวดใน BOT API | ใช้กับ |
|---|---|---|
| `BOT_API_TOKEN_3` | Exchange Rates | `usd_thb` ส่งให้โค้ดเป็น `BOT_TOKEN_EXCHANGE` |
| `BOT_API_TOKEN` | Statistics | ยังไม่ได้ใช้ |
| `BOT_API_TOKEN_2` | Policy Rate | วันประชุม กนง. ล่าสุดของ `policy_rate` ส่งให้โค้ดเป็น `BOT_TOKEN_POLICY` |

## โครงสร้าง

```
src/series.py       # รายการตัวชี้วัด
src/sources.py      # BIS (ไม่ต้องใช้ key) และตัวช่วยเรียก HTTP
src/bot_api.py      # BOT API อ่าน token ของแต่ละหมวดจากตัวแปรของตัวเอง
src/sample_data.py  # ข้อมูลตัวอย่างสำหรับรันแบบออฟไลน์
src/build_data.py   # ดึงทุกตัวชี้วัด ตรวจความสด แล้วเขียน JSON
tests/              # pytest
web/                # หน้าเว็บ React + TypeScript (Vite)
```

## License
[MIT](LICENSE). ข้อมูลเศรษฐกิจเป็นของธนาคารแห่งประเทศไทยและ BIS ใช้ตามเงื่อนไขของ BOT API Portal และ BIS
