import { useEffect, useRef } from 'react'
import type { Lang } from '../data'
import type { Range } from '../derive'
import { RANGES } from '../derive'
import type { Strings } from '../i18n'
import { formatLongDate } from '../i18n'

export type Theme = 'light' | 'dark'

interface Props {
  t: Strings
  lang: Lang
  /** The moment the data file was written, or empty while it is still loading. */
  generated: string
  range: Range
  onRange: (r: Range) => void
  query: string
  onQuery: (q: string) => void
  theme: Theme
  onTheme: () => void
  onLang: () => void
  onRefresh: () => void
}

export function TopBar({ t, lang, generated, range, onRange, query, onQuery, theme, onTheme, onLang, onRefresh }: Props) {
  const box = useRef<HTMLInputElement>(null)
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== '/' || e.metaKey || e.ctrlKey || e.altKey) return
      if (document.activeElement === box.current) return
      e.preventDefault()
      box.current?.focus()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

  return (
    <header className="topbar">
      <div className="topbar-inner">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true">฿</span>
          <span className="brand-text">
            <h1>{t.title}</h1>
            {generated && <small>{formatLongDate(generated, lang)}</small>}
          </span>
        </div>
        <label className="search">
          <svg className="icon" viewBox="0 0 24 24" aria-hidden="true">
            <circle cx="11" cy="11" r="7" /><path d="m20 20-3.5-3.5" />
          </svg>
          <input ref={box} type="search" value={query} placeholder={t.search} aria-label={t.searchLabel}
            onChange={(e) => onQuery(e.target.value)} />
          <kbd aria-hidden="true">/</kbd>
        </label>
        <div className="actions">
          <div className="segmented" role="group" aria-label={t.range}>
            {(Object.keys(RANGES) as Range[]).map((r) => (
              <button key={r} aria-pressed={r === range} onClick={() => onRange(r)}>{r}</button>
            ))}
          </div>
          <button className="icon-btn" aria-label={t.refresh} onClick={onRefresh}>
            <svg className="icon" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M21 12a9 9 0 1 1-2.6-6.4" /><path d="M21 4v5h-5" />
            </svg>
          </button>
          <button className="icon-btn" aria-label={t.theme} aria-pressed={theme === 'dark'} onClick={onTheme}>
            <svg className="icon" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z" />
            </svg>
          </button>
          <button className="icon-btn text" aria-label={t.langLabel} onClick={onLang}>{t.langButton}</button>
        </div>
      </div>
    </header>
  )
}
