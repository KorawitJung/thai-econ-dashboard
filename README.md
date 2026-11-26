# Thailand macro dashboard

เปิดดู dashboard ได้ที่ https://korawitjung.github.io/thai-econ-dashboard

หน้าเว็บนี้แสดงค่าเงินบาท ดอกเบี้ย เงินเฟ้อ และตัวเลขเศรษฐกิจไทย 20 ตัว เปิดได้ทั้งบนมือถือ iPad และคอมพิวเตอร์ ถ้าจะเปิดบน iPad แบบแอป ให้เปิดลิงก์ใน Safari กดปุ่มแชร์ แล้วเลือก "เพิ่มไปยังหน้าจอโฮม"

> **คำเตือน / Disclaimer**
> โปรเจกต์นี้ทำขึ้น **เพื่อการศึกษาเท่านั้น** ไม่ได้ใช้ในเชิงพาณิชย์ ไม่ใช่คำแนะนำการลงทุน
> และไม่ได้มีเจตนาทำให้บุคคลหรือองค์กรใดเสียหาย ข้อมูลเป็นของธนาคารแห่งประเทศไทย (ธปท.)
> และ BIS ตามที่ระบุในตารางด้านล่าง โปรดตรวจสอบตัวเลขกับแหล่งข้อมูลทางการก่อนนำไปใช้ทุกครั้ง
>
> *For educational purposes only. Not for commercial use, not investment advice, and not
> intended to harm any person or organization. Data belongs to the Bank of Thailand and the BIS,
> as listed below.*

สคริปต์ Python ดึงข้อมูลจาก BOT API และ BIS แล้วเขียนเป็นไฟล์ JSON ไฟล์เดียว หน้าเว็บอ่านไฟล์นี้ไปแสดง

หน้าเว็บเขียนด้วย React + TypeScript ใช้สีและตัวอักษรแบบแอป iOS มีภาษาไทยและอังกฤษ และเปลี่ยนเป็น dark mode ตามการตั้งค่าของเครื่อง

บนมือถือ หน้าแรกเป็นรายการตัวชี้วัด กดแถวไหนก็เข้าไปดูกราฟของตัวนั้น บนจอกว้างตั้งแต่ 700 px เช่น iPad และคอมพิวเตอร์ รายการอยู่ทางซ้ายและกราฟของตัวที่เลือกอยู่ทางขวา

GitHub Actions ดึงข้อมูลใหม่และเผยแพร่หน้าเว็บบน GitHub Pages ทุกวัน

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

ธปท. เผยแพร่ข้อมูลรายเดือนหลังสิ้นเดือนนั้นหนึ่งถึงสามเดือน และใช้วันแรกของเดือนเป็นวันที่ของข้อมูล สคริปต์จึงยอมให้ข้อมูลรายเดือนเก่าได้ถึง 150 วัน

ดอกเบี้ย อัตราการว่างงาน ดุลการค้า และดุลบัญชีเดินสะพัด แสดงการเปลี่ยนแปลงเป็นผลต่าง เพราะร้อยละของตัวเลขที่ติดลบได้ไม่มีความหมาย ตัวอื่นแสดงเป็นร้อยละ

BIS ไม่ต้องใช้ key และอนุญาตให้เผยแพร่ข้อมูลต่อเพื่อการที่ไม่ใช่เชิงพาณิชย์ หน้ารายละเอียดของแต่ละตัวชี้วัดบอกแหล่งที่มาไว้ที่บรรทัดล่างสุด

แต่ละแอปใน BOT API Portal มี token ของตัวเองและ subscribe ได้หมวดเดียว โค้ดจึงอ่าน token ของแต่ละหมวดจากตัวแปรแยกกัน

| หมวดใน BOT API | ตัวแปร | ใช้กับ |
|---|---|---|
| Exchange Rates | `BOT_TOKEN_EXCHANGE` | ค่าเงินห้าสกุล |
| Policy Rate | `BOT_TOKEN_POLICY` | วันประชุมและมติ กนง. |
| Statistics | `BOT_TOKEN_STATISTICS` | ตัวชี้วัดอื่นของ ธปท. |

กราฟดอกเบี้ยนโยบายใช้ข้อมูลจาก BIS เพราะ `/PolicyRate/v3` ของ BOT API ให้แค่อัตราล่าสุด ไม่มีประวัติย้อนหลัง ส่วนวันประชุมและข้อความมติมาจาก BOT API เพราะบอกวันประชุมครั้งล่าสุดได้ แม้มติครั้งนั้นจะคงอัตราไว้

BOT API ไม่มีเงินเฟ้อทั่วไปของทั้งประเทศ CPI จึงใช้ข้อมูลจาก BIS

การเพิ่มตัวชี้วัดใหม่มีสองขั้น ขั้นแรกเพิ่มหนึ่งบรรทัดใน `SERIES` ชุดข้อมูลของ ธปท. ใช้ `stat(...)` กับรหัสชุดข้อมูลที่หาได้ใน [BOT API Portal](https://portal.api.bot.or.th) ส่วนสกุลเงินใช้ `fx(...)` ขั้นที่สองเพิ่มค่าตัวอย่างของตัวชี้วัดนั้นใน `src/sample_data.py`

## วิธีใช้

```bash
pip install -r requirements-dev.txt
python src/build_data.py --sample   # ข้อมูลตัวอย่าง ไม่ต้องมี token
pytest -q tests
```

`python src/build_data.py` ดึงข้อมูลจริงจากแหล่งข้างบน ก่อนรันต้องตั้งตัวแปร `BOT_TOKEN_STATISTICS` `BOT_TOKEN_EXCHANGE` และ `BOT_TOKEN_POLICY`

สคริปต์เขียนไฟล์ไว้ที่ `web/public/data/dashboard.json` ถ้าจะเขียนที่อื่นให้ใช้ `--out`

ถ้าแหล่งใดตอบ error หรือข้อมูลล่าสุดเก่ากว่าที่กำหนดในตารางข้างบน สคริปต์จะหยุด บอกสาเหตุ และไม่เขียนไฟล์

ข้อมูลตัวอย่างไม่ใช่ตัวเลขจริงของ ธปท. ไฟล์ที่สร้างจากข้อมูลตัวอย่างมี `"source": "sample"` และหน้าเว็บแสดงป้ายว่าเป็นข้อมูลตัวอย่าง

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

URL ของหน้ารายละเอียดมี hash เช่น `#usd_thb` ปุ่มย้อนกลับของเบราว์เซอร์จึงใช้ได้ และส่งลิงก์ของตัวชี้วัดตัวใดตัวหนึ่งให้คนอื่นได้

## GitHub Actions

`.github/workflows/update.yml` รัน test ของ Python และหน้าเว็บทุกครั้งที่ push หรือเปิด pull request

ทุกวันเวลาประมาณ 18:00 น. ตามเวลาไทย workflow นี้ดึงข้อมูลจริง build หน้าเว็บ แล้วเผยแพร่ขึ้น GitHub Pages ปกติ GitHub เริ่มรันช้ากว่าเวลาที่ตั้งไว้

ก่อนรันครั้งแรกต้องเปิด GitHub Pages โดยไปที่ Settings ของ repo เลือก Pages แล้วตั้ง Source เป็น GitHub Actions

ขั้นดึงข้อมูลจริงใช้ repository secret ตั้งได้ที่ Settings ของ repo เลือก Secrets and variables แล้วเลือก Actions

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
