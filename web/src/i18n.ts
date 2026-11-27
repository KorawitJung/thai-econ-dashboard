import type { Lang } from './data'

export const STRINGS = {
  th: {
    title: 'เศรษฐกิจไทย',
    updated: 'อัปเดต',
    sample: 'ข้อมูลตัวอย่าง ไม่ใช่ตัวเลขจริง',
    latest: 'ล่าสุด',
    lastMove: 'ครั้งล่าสุด',
    lastMeeting: 'ประชุม กนง. ล่าสุด',
    indicators: 'ตัวชี้วัด',
    meetingSource: 'มติ กนง.: ธนาคารแห่งประเทศไทย',
    high: 'สูงสุด',
    low: 'ต่ำสุด',
    over: 'ในช่วง',
    since: 'ตั้งแต่',
    asOf: 'ข้อมูล ณ',
    sourceLabel: 'ที่มา:',
    sampleSource: 'ข้อมูลตัวอย่างที่สร้างขึ้นเอง',
    langButton: 'EN',
    langLabel: 'Switch to English',
    range: 'ช่วงเวลา',
    search: 'ค้นหาตัวชี้วัด เช่น ดอลลาร์ ส่งออก…',
    searchLabel: 'ค้นหาตัวชี้วัด กด / เพื่อไปที่ช่องค้นหา',
    all: 'ทั้งหมด',
    groupLabel: 'เลือกหมวด',
    summary: 'สรุปภาพรวม · Overview',
    summaryBadge: 'คำนวณจากตัวเลขจริง',
    summaryToggle: 'ย่อหรือขยายสรุปภาพรวม',
    refresh: 'โหลดข้อมูลใหม่',
    theme: 'โหมดมืด',
    close: 'ปิด',
    none: 'ไม่พบตัวชี้วัด',
    loading: 'กำลังโหลด…',
    failed: 'โหลดข้อมูลไม่สำเร็จ',
    retry: 'ลองอีกครั้ง',
    disclaimer: 'เพื่อการศึกษาเท่านั้น ไม่ใช่คำแนะนำการลงทุน',
  },
  en: {
    title: 'Thai economy',
    updated: 'Updated',
    sample: 'Sample data, not real figures',
    latest: 'Latest',
    lastMove: 'Last move',
    lastMeeting: 'Last MPC meeting',
    indicators: 'Indicators',
    meetingSource: 'MPC decision: Bank of Thailand',
    high: 'High',
    low: 'Low',
    over: 'over',
    since: 'since',
    asOf: 'As of',
    sourceLabel: 'Source:',
    sampleSource: 'Synthetic sample data',
    langButton: 'ไทย',
    langLabel: 'เปลี่ยนเป็นภาษาไทย',
    range: 'Range',
    search: 'Search indicators, e.g. dollar, exports…',
    searchLabel: 'Search indicators, press / to jump to the search box',
    all: 'All',
    groupLabel: 'Pick a category',
    summary: 'สรุปภาพรวม · Overview',
    summaryBadge: 'Computed from real data',
    summaryToggle: 'Collapse or expand the overview',
    refresh: 'Reload the data',
    theme: 'Dark mode',
    close: 'Close',
    none: 'No indicator found',
    loading: 'Loading…',
    failed: 'Could not load the data',
    retry: 'Try again',
    disclaimer: 'For education only. Not investment advice.',
  },
} satisfies Record<Lang, Record<string, string>>

export type Strings = (typeof STRINGS)[Lang]

const locale = (lang: Lang) => (lang === 'th' ? 'th-TH' : 'en-GB')

export function formatDateTime(iso: string, lang: Lang): string {
  return new Intl.DateTimeFormat(locale(lang), {
    day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', timeZone: 'Asia/Bangkok',
  }).format(new Date(iso))
}

export function formatDate(day: string, lang: Lang): string {
  return new Intl.DateTimeFormat(locale(lang), {
    day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC',
  }).format(new Date(`${day}T00:00:00Z`))
}

/** The day the data speaks for, spelled out under the title in the top bar. */
export function formatLongDate(iso: string, lang: Lang): string {
  return new Intl.DateTimeFormat(locale(lang), {
    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric', timeZone: 'Asia/Bangkok',
  }).format(new Date(iso))
}
