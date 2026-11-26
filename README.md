# Thailand Macro Dashboard: ค่าเงินบาท · ดอกเบี้ย · เงินเฟ้อ · เศรษฐกิจ

**เปิดดู dashboard: https://korawitjung.github.io/thai-econ-dashboard**

ใช้ได้ทั้งมือถือ iPad และคอมพิวเตอร์ บน iPad เปิดใน Safari แล้วกด **แชร์ → เพิ่มไปยังหน้าจอโฮม** เพื่อเปิดแบบแอปได้

> ⚠️ **คำเตือน / Disclaimer**
> โปรเจกต์นี้ทำขึ้น **เพื่อการศึกษาเท่านั้น** ไม่ได้ใช้ในเชิงพาณิชย์ ไม่ใช่คำแนะนำการลงทุน
> และไม่ได้มีเจตนาทำให้บุคคลหรือองค์กรใดเสียหาย ข้อมูลเป็นของธนาคารแห่งประเทศไทย (ธปท.)
> และ BIS ตามที่ระบุในตารางด้านล่าง โปรดตรวจสอบตัวเลขกับแหล่งข้อมูลทางการก่อนนำไปใช้ทุกครั้ง
>
> *For educational purposes only. Not for commercial use, not investment advice, and not
> intended to harm any person or organization. Data belongs to the Bank of Thailand and the BIS,
> as listed below.*

ดึงข้อมูลเศรษฐกิจไทยจาก BOT API และ BIS ด้วย Python แล้วเขียนเป็นไฟล์ JSON ไฟล์เดียว ให้หน้าเว็บนำไปแสดง

หน้าเว็บเขียนด้วย React + TypeScript หน้าตาแบบแอป iOS มีภาษาไทยและอังกฤษ และเปลี่ยนเป็น dark mode ตามเครื่อง บนมือถือเป็นรายการแล้วกดเข้าไปดูรายละเอียด จอตั้งแต่ 700 px ขึ้นไป เช่น iPad และคอมพิวเตอร์ จะแสดงรายการทางซ้ายและกราฟทางขวาพร้อมกัน GitHub Actions สร้างข้อมูลและเผยแพร่บน GitHub Pages ทุกวัน

## ข้อมูลที่ดึง

ตัวชี้วัดทั้งหมดอยู่ใน `src/series.py` ไฟล์เดียว ตัวละหนึ่งรายการ

| หมวด | id | ข้อมูล | แหล่ง | ความถี่ | ถือว่าเก่าเกินเมื่อ |
|---|---|---|---|---|---|
| ค่าเงินบาท | `usd_thb` `eur_thb` `jpy_thb` `cny_thb` `gbp_thb` | อัตรากลาง เฉลี่ยรายวัน (เยนคิดต่อ 100 เยน) | [BOT API](https://portal.api.bot.or.th) Exchange Rates | รายวัน | เกิน 7 วัน |
| ค่าเงินบาท | `neer` | ดัชนีค่าเงินบาทเทียบคู่ค้า (NEER) | BOT API Statistics `EINEERM00071` | รายเดือน | เกิน 150 วัน |
| ดอกเบี้ย | `policy_rate` | ดอกเบี้ยนโยบาย วันประชุม และมติ กนง. ล่าสุด | อัตรา: [BIS Data Portal](https://data.bis.org) `WS_CBPOL` จากข้อมูลของ ธปท. มติ: BOT API Policy Rate | ตามมติ กนง. | ไม่ตรวจ |
| ดอกเบี้ย | `thor` | อัตราดอกเบี้ยข้ามคืน THOR | BOT API Statistics `FMRTTHORD00003` | รายวัน | เกิน 7 วัน |
| ดอกเบี้ย | `bond_10y` | อัตราผลตอบแทนพันธบัตรรัฐบาล 10 ปี | BOT API Statistics `FMRTINTM00296` | รายเดือน | เกิน 150 วัน |
| เงินเฟ้อ | `cpi_yoy` | เงินเฟ้อทั่วไป YoY | [BIS Data Portal](https://data.bis.org) `WS_LONG_CPI` | รายเดือน | เกิน 120 วัน |
| เศรษฐกิจในประเทศ | `consumption` | ดัชนีการบริโภคภาคเอกชน ปรับฤดูกาล | BOT API Statistics `EIPCIM00063` | รายเดือน | เกิน 150 วัน |
| เศรษฐกิจในประเทศ | `investment` | ดัชนีการลงทุนภาคเอกชน ปรับฤดูกาล | BOT API Statistics `EIPIIM00061` | รายเดือน | เกิน 150 วัน |
| เศรษฐกิจในประเทศ | `manufacturing` | ดัชนีผลผลิตอุตสาหกรรม ปรับฤดูกาล | BOT API Statistics `RGNRMPIM00002` | รายเดือน | เกิน 150 วัน |
| เศรษฐกิจในประเทศ | `sentiment` | ดัชนีความเชื่อมั่นภาคธุรกิจ | BOT API Statistics `EIBSIM00057` | รายเดือน | เกิน 150 วัน |
| เศรษฐกิจในประเทศ | `unemployment` | อัตราการว่างงาน | BOT API Statistics `RLLFSWKM00079` | รายเดือน | เกิน 150 วัน |
| เศรษฐกิจในประเทศ | `tourists` | นักท่องเที่ยวต่างชาติ (ล้านคน) | BOT API Statistics `EITOURISTM00267` | รายเดือน | เกิน 150 วัน |
| ภาคต่างประเทศ | `exports` | มูลค่าส่งออก (พันล้านดอลลาร์) | BOT API Statistics `XTBOP0OVL0M15593` | รายเดือน | เกิน 150 วัน |
| ภาคต่างประเทศ | `trade_balance` | ดุลการค้า (พันล้านดอลลาร์) | BOT API Statistics `XTBOP0OVL0M15595` | รายเดือน | เกิน 150 วัน |
| ภาคต่างประเทศ | `current_account` | ดุลบัญชีเดินสะพัด (พันล้านดอลลาร์) | BOT API Statistics `XTBOP0OVL0M15597` | รายเดือน | เกิน 150 วัน |
| ภาคต่างประเทศ | `reserves` | ทุนสำรองระหว่างประเทศ ส่วนเงินตราต่างประเทศ (พันล้านดอลลาร์) | BOT API Statistics `XTRSV00000M00697` | รายเดือน | เกิน 150 วัน |

ข้อมูลรายเดือนของ ธปท. ออกช้ากว่าเดือนจริงหนึ่งถึงสามเดือน และลงวันที่เป็นวันแรกของเดือน จึงยอมให้เก่าได้ถึง 150 วัน ดอกเบี้ย อัตราการว่างงาน ดุลการค้า และดุลบัญชีเดินสะพัด แสดงการเปลี่ยนแปลงเป็นผลต่าง ตัวอื่นแสดงเป็นร้อยละ

BIS ไม่ต้องใช้ key และอนุญาตให้นำข้อมูลไปเผยแพร่ต่อเพื่อการที่ไม่ใช่เชิงพาณิชย์ หน้าเว็บระบุแหล่งที่มาไว้ที่ตัวชี้วัดแต่ละตัว

BOT API ใช้ token แยกตามแอปใน portal และแต่ละแอป subscribe หมวดเดียว ค่าเงินใช้หมวด Exchange Rates โค้ดอ่าน token จากตัวแปร `BOT_TOKEN_EXCHANGE` มติ กนง. ใช้หมวด Policy Rate อ่านจาก `BOT_TOKEN_POLICY` ตัวชี้วัดอื่นของ ธปท. ใช้หมวด Statistics อ่านจาก `BOT_TOKEN_STATISTICS`

กราฟดอกเบี้ยนโยบายยังใช้ BIS เพราะ BOT API รุ่นปัจจุบัน (`/PolicyRate/v3`) ให้แค่ค่าล่าสุด ไม่มีประวัติย้อนหลัง แต่ให้วันประกาศและข้อความมติครั้งล่าสุด ซึ่งบอกวันประชุมได้แม้มตินั้นจะคงอัตราไว้ และ BOT ไม่มีเงินเฟ้อทั่วไปของทั้งประเทศ CPI จึงใช้ BIS เช่นกัน

เพิ่มตัวชี้วัดใหม่ได้โดยเพิ่มหนึ่งบรรทัดใน `SERIES` ชุดข้อมูลของ ธปท. ใช้ `stat(...)` กับรหัสชุดข้อมูลจาก [BOT API Portal](https://portal.api.bot.or.th) สกุลเงินใช้ `fx(...)` แล้วเพิ่มค่าตัวอย่างใน `src/sample_data.py`

## วิธีใช้

```bash
pip install -r requirements-dev.txt
python src/build_data.py --sample   # ข้อมูลตัวอย่าง ไม่ต้องมี token
pytest -q tests
```

`python src/build_data.py` ดึงข้อมูลจริงจากแหล่งข้างบน ต้องตั้งตัวแปร `BOT_TOKEN_STATISTICS` `BOT_TOKEN_EXCHANGE` และ `BOT_TOKEN_POLICY` ก่อน

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
| `web/src/App.tsx` | โหลดข้อมูล เลือกตัวชี้วัดจาก URL และสลับระหว่างแบบมือถือกับแบบสองคอลัมน์ |
| `web/src/components/Overview.tsx` | รายการตัวชี้วัด แบ่งหมวดพร้อมกราฟเล็ก |
| `web/src/components/Detail.tsx` | รายละเอียด กราฟใหญ่ เลือก 6M / 1Y / 3Y และมติ กนง. |
| `web/src/i18n.ts` | ข้อความภาษาไทยและอังกฤษ |

หน้ารายละเอียดใช้ hash ใน URL เช่น `#usd_thb` จึงกดปุ่มย้อนกลับของเบราว์เซอร์และแชร์ลิงก์ได้

## GitHub Actions

`.github/workflows/update.yml` รัน test ของ Python และหน้าเว็บทุก push และ pull request ทุกวันเวลาประมาณ 18:00 น. ตามเวลาไทย (GitHub มักเริ่มช้ากว่านั้น) จะดึงข้อมูลจริง build หน้าเว็บ แล้วเผยแพร่ขึ้น GitHub Pages

ต้องเปิด GitHub Pages ก่อนครั้งแรก ที่ **Settings → Pages → Source** ให้เลือก **GitHub Actions**

ขั้นดึงข้อมูลจริงใช้ repository secret ที่ **Settings → Secrets and variables → Actions**

| Secret | หมวดใน BOT API | ใช้กับ |
|---|---|---|
| `BOT_API_TOKEN` | Statistics | `neer` `thor` `bond_10y` และหมวดเศรษฐกิจในประเทศกับภาคต่างประเทศ ส่งให้โค้ดเป็น `BOT_TOKEN_STATISTICS` |
| `BOT_API_TOKEN_2` | Policy Rate | วันประชุมและมติ กนง. ล่าสุดของ `policy_rate` ส่งให้โค้ดเป็น `BOT_TOKEN_POLICY` |
| `BOT_API_TOKEN_3` | Exchange Rates | ค่าเงินทั้งห้าสกุล ส่งให้โค้ดเป็น `BOT_TOKEN_EXCHANGE` |

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
