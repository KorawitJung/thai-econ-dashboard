import { useEffect, useRef } from 'react'
import type { Dashboard, Lang, Series } from '../data'
import type { Range } from '../derive'
import { coversRange, direction, formatChange, formatValue, last, latestChange, rangeChange, windowed } from '../derive'
import type { Strings } from '../i18n'
import { formatDate } from '../i18n'
import { Chart } from './Chart'

interface Props {
  data: Dashboard
  series: Series
  lang: Lang
  t: Strings
  range: Range
  onClose: () => void
}

export function Detail({ data, series: s, lang, t, range, onClose }: Props) {
  const card = useRef<HTMLElement>(null)
  // A link such as #policy_rate opens a card that can sit far down the page.
  useEffect(() => {
    card.current?.scrollIntoView({ block: 'nearest' })
  }, [])

  const pts = windowed(s, range)
  const change = rangeChange(s, pts)
  const move = latestChange(s)
  const values = pts.map(([, v]) => v)
  const group = data.groups.find((g) => g.id === s.group)
  const span = coversRange(s, pts, range) ? `${t.over} ${range}` : `${t.since} ${formatDate(pts[0]![0], lang)}`
  return (
    <article className={`card detail tint-${s.group}`} ref={card} aria-labelledby={`detail-${s.id}`}>
      <button className="icon-btn close" aria-label={t.close} onClick={onClose}>
        <svg className="icon" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 6 18 18M18 6 6 18" /></svg>
      </button>
      {group && <span className="tag">{group.name[lang]}</span>}
      <h4 id={`detail-${s.id}`}>{s.name[lang]}</h4>
      <p className="muted">{s.sub[lang]}</p>
      <p className="headline">
        <span className="num">{formatValue(s, last(s)[1])}</span>
        <span className={`pill ${direction(change)}`}>{formatChange(change)} {span}</span>
      </p>
      <Chart points={pts} width={800} height={300} stepped={s.frequency === 'event'}
        label={`${s.name[lang]} ${formatChange(change)} ${span}`} />
      <dl className="statrow">
        <div className="stat"><dt>{t.latest}</dt><dd>{formatValue(s, last(s)[1])}</dd></div>
        <div className="stat"><dt>{t.lastMove}</dt><dd className={`fg-${direction(move)}`}>{formatChange(move)}</dd></div>
        <div className="stat"><dt>{t.high}</dt><dd>{formatValue(s, Math.max(...values))}</dd></div>
        <div className="stat"><dt>{t.low}</dt><dd>{formatValue(s, Math.min(...values))}</dd></div>
      </dl>
      {s.meeting && (
        <section className="meeting" aria-label={t.lastMeeting}>
          <p className="meeting-head"><span>{t.lastMeeting}</span><strong>{formatDate(s.meeting.date, lang)}</strong></p>
          <p className="decision">{s.meeting.decision[lang]}</p>
        </section>
      )}
      <p className="source">
        {t.asOf} {formatDate(last(s)[0], lang)} · {data.source === 'sample' ? t.sampleSource : `${t.sourceLabel} ${s.source[lang]}`}
        {s.meeting && data.source !== 'sample' && ` · ${t.meetingSource}`}
      </p>
    </article>
  )
}
