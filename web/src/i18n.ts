import type { Lang } from './data'

export const STRINGS = {
  th: {
    title: 'เศรษฐกิจไทย',
    updated: 'อัปเดต',
    sample: 'ข้อมูลตัวอย่าง ไม่ใช่ตัวเลขจริงของ ธปท.',
    back: 'ภาพรวม',
    latest: 'ล่าสุด',
    lastMove: 'ครั้งล่าสุด',
    high: 'สูงสุด',
    low: 'ต่ำสุด',
    over: 'ในช่วง',
    asOf: 'ข้อมูล ณ',
    source: 'ที่มา: ธนาคารแห่งประเทศไทย (BOT API)',
    sampleSource: 'ข้อมูลตัวอย่างที่สร้างขึ้นเอง',
    langButton: 'EN',
    langLabel: 'Switch to English',
    range: 'ช่วงเวลา',
    loading: 'กำลังโหลด…',
    failed: 'โหลดข้อมูลไม่สำเร็จ',
    retry: 'ลองอีกครั้ง',
    notFound: 'ไม่พบตัวชี้วัดนี้',
    disclaimer: 'เพื่อการศึกษาเท่านั้น ไม่ใช่คำแนะนำการลงทุน',
  },
  en: {
    title: 'Thai economy',
    updated: 'Updated',
    sample: 'Sample data, not real Bank of Thailand figures',
    back: 'Overview',
    latest: 'Latest',
    lastMove: 'Last move',
    high: 'High',
    low: 'Low',
    over: 'over',
    asOf: 'As of',
    source: 'Source: Bank of Thailand (BOT API)',
    sampleSource: 'Synthetic sample data',
    langButton: 'ไทย',
    langLabel: 'เปลี่ยนเป็นภาษาไทย',
    range: 'Range',
    loading: 'Loading…',
    failed: 'Could not load the data',
    retry: 'Try again',
    notFound: 'This indicator was not found',
    disclaimer: 'For education only. Not investment advice.',
  },
} satisfies Record<Lang, Record<string, string>>

export type Strings = (typeof STRINGS)[Lang]

export function formatDateTime(iso: string, lang: Lang): string {
  return new Intl.DateTimeFormat(lang === 'th' ? 'th-TH' : 'en-GB', {
    day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit', timeZone: 'Asia/Bangkok',
  }).format(new Date(iso))
}

export function formatDate(day: string, lang: Lang): string {
  return new Intl.DateTimeFormat(lang === 'th' ? 'th-TH' : 'en-GB', {
    day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC',
  }).format(new Date(`${day}T00:00:00Z`))
}
