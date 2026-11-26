import type { ReactNode } from 'react'
import { useEffect, useRef } from 'react'
import type { Dashboard, Lang } from '../data'
import { direction, formatChange, formatValue, last, latestChange, rangeChange, sparkPoints } from '../derive'
import type { Strings } from '../i18n'
import { formatDateTime } from '../i18n'
import { Sparkline } from './Sparkline'

interface Props {
  data: Dashboard
  lang: Lang
  t: Strings
  onOpen: (id: string) => void
  langButton: ReactNode
  /** In split view, the series shown beside the list. */
  selected?: string
}

export function Overview({ data, lang, t, onOpen, langButton, selected }: Props) {
  const current = useRef<HTMLButtonElement>(null)
  // A shared link can open an indicator far down the list, so scroll its row into view.
  useEffect(() => {
    current.current?.scrollIntoView({ block: 'nearest' })
  }, [selected])
  return (
    <div className="screen">
      <div className="toolbar end">{langButton}</div>
      <header className="large-title">
        <h1>{t.title}</h1>
        <p className="meta">{t.updated} {formatDateTime(data.generated, lang)}</p>
      </header>
      {data.source === 'sample' && <p className="sample-note" role="note">{t.sample}</p>}
      {data.groups.map((g) => {
        const rows = data.series.filter((s) => s.group === g.id)
        if (rows.length === 0) return null
        return (
          <section key={g.id} className="group" aria-labelledby={`g-${g.id}`}>
            <h2 id={`g-${g.id}`}>{g.name[lang]}</h2>
            <ul className="card list">
              {rows.map((s) => {
                const ch = latestChange(s)
                const tone = direction(ch)
                const spark = sparkPoints(s)
                return (
                  <li key={s.id}>
                    <button className="row" onClick={() => onOpen(s.id)}
                      aria-current={s.id === selected || undefined} ref={s.id === selected ? current : undefined}>
                      <span className="row-label">
                        <span className="row-name">{s.name[lang]}</span>
                        <span className="row-sub">{s.sub[lang]}</span>
                      </span>
                      <Sparkline points={spark} stepped={s.frequency === 'event'} tone={direction(rangeChange(s, spark))} />
                      <span className="row-figures">
                        <span className="row-value">{formatValue(s, last(s)[1])}</span>
                        <span className={`pill bg-${tone}`}>{formatChange(ch)}</span>
                      </span>
                    </button>
                  </li>
                )
              })}
            </ul>
          </section>
        )
      })}
      <p className="footnote">{t.disclaimer}</p>
    </div>
  )
}
