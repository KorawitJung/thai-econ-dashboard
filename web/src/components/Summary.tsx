import { useEffect, useState } from 'react'
import type { SummaryLine } from '../data'
import type { Strings } from '../i18n'

const PHONE = '(max-width: 759px)'

export function Summary({ lines, t }: { lines: SummaryLine[]; t: Strings }) {
  // On a phone the five sentences fill the first screen, so they start folded away there.
  const [open, setOpen] = useState(() => !window.matchMedia(PHONE).matches)
  useEffect(() => {
    const phone = window.matchMedia(PHONE)
    const sync = () => setOpen(!phone.matches)
    phone.addEventListener('change', sync)
    return () => phone.removeEventListener('change', sync)
  }, [])

  return (
    <section className="brief" aria-labelledby="brief-title">
      <div className="brief-head">
        <h2 id="brief-title">{t.summary}</h2>
        <span className="brief-badge">{t.summaryBadge}</span>
        <button className="brief-toggle" aria-label={t.summaryToggle} aria-expanded={open}
          aria-controls="brief-lines" onClick={() => setOpen(!open)}>
          <svg className="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="m6 9 6 6 6-6" /></svg>
        </button>
      </div>
      <ol id="brief-lines" hidden={!open}>
        {lines.map((l, i) => (
          <li key={l.group} className={`tint-${l.group}`}>
            <span className="n" aria-hidden="true">{i + 1}</span>
            <div>
              <p className="th" lang="th">{l.th}</p>
              <p className="en" lang="en">{l.en}</p>
            </div>
          </li>
        ))}
      </ol>
    </section>
  )
}
