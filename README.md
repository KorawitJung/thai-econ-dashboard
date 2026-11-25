# Thailand Macro Dashboard: ค่าเงินบาท · เงินเฟ้อ · ดอกเบี้ยนโยบาย

> ⚠️ **คำเตือน / Disclaimer**
> โปรเจกต์นี้ทำขึ้น **เพื่อการศึกษาเท่านั้น** ไม่ได้ใช้ในเชิงพาณิชย์ ไม่ใช่คำแนะนำการลงทุน
> และไม่ได้มีเจตนาทำให้บุคคลหรือองค์กรใดเสียหาย ข้อมูลเป็นของธนาคารแห่งประเทศไทย (ธปท.)
> โปรดตรวจสอบตัวเลขกับแหล่งข้อมูลทางการก่อนนำไปใช้ทุกครั้ง
>
> *For educational purposes only. Not for commercial use, not investment advice, and not
> intended to harm any person or organization. Data belongs to the Bank of Thailand.*

ดึงข้อมูลจาก [BOT API Portal](https://portal.api.bot.or.th) ด้วย Python แล้วเขียนเป็นไฟล์ JSON ไฟล์เดียว ให้หน้าเว็บนำไปแสดง

## ข้อมูลที่ดึง

ตัวชี้วัดทั้งหมดอยู่ใน `src/series.py` ไฟล์เดียว ตัวละหนึ่งรายการ

| id | ข้อมูล | ความถี่ | ถือว่าเก่าเกินเมื่อ |
|---|---|---|---|
| `usd_thb` | อัตราแลกเปลี่ยน USD/THB (mid rate) | รายวัน | เกิน 7 วัน |
| `policy_rate` | ดอกเบี้ยนโยบาย | ตามมติ กนง. | ไม่ตรวจ |
| `cpi_yoy` | เงินเฟ้อทั่วไป YoY | รายเดือน | เกิน 95 วัน |

เพิ่มตัวชี้วัดใหม่ได้โดยเพิ่ม `Series` หนึ่งรายการใน `SERIES` พร้อมฟังก์ชันดึงข้อมูลที่คืนคอลัมน์ `date` และ `value`

## วิธีใช้

```bash
pip install -r requirements-dev.txt
python src/build_data.py --sample   # ข้อมูลตัวอย่าง ไม่ต้องมี token
pytest -q tests
```

ถ้าจะใช้ข้อมูลจริง ให้ขอ token ฟรีที่ https://portal.api.bot.or.th แล้วตั้ง environment variable `BOT_API_TOKEN` ก่อนรัน `python src/build_data.py`

ไฟล์จะออกที่ `web/public/data/dashboard.json` เปลี่ยนที่ได้ด้วย `--out`

ถ้าไม่มี token, API ตอบ error หรือข้อมูลล่าสุดเก่ากว่าที่กำหนดในตารางข้างบน สคริปต์จะหยุดพร้อมบอกสาเหตุ และไม่เขียนไฟล์ ข้อมูลตัวอย่าง **ไม่ใช่ตัวเลขจริงของ ธปท.** และไฟล์จะมี `"source": "sample"` กำกับไว้

ถ้า ธปท. เปลี่ยน path ของ API ให้แก้ผ่าน env ได้: `BOT_EXG_PATH`, `BOT_POLICY_PATH`, `BOT_OBS_PATH`, `BOT_CPI_SERIES`

## GitHub Actions

`.github/workflows/update.yml` รัน test ทุก push และ pull request แล้วดึงข้อมูลจริงทุกวันเวลา 18:00 น. ตามเวลาไทย

ให้เพิ่ม secret ชื่อ `BOT_API_TOKEN` ที่ **Settings → Secrets and variables → Actions → Repository secrets** ถ้าไม่มี secret งานดึงข้อมูลจริงจะขึ้นสีแดง

## โครงสร้าง

```
src/series.py       # รายการตัวชี้วัด
src/bot_api.py      # client เรียก BOT API
src/sample_data.py  # ข้อมูลตัวอย่างสำหรับรันแบบออฟไลน์
src/build_data.py   # ดึงทุกตัวชี้วัด ตรวจความสด แล้วเขียน JSON
tests/              # pytest
```

## License
[MIT](LICENSE). ข้อมูลเศรษฐกิจเป็นลิขสิทธิ์ของธนาคารแห่งประเทศไทย ใช้ตามเงื่อนไขของ BOT API Portal
