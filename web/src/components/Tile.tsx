import type { Lang, Series } from '../data'
import type { Range } from '../derive'
import { direction, formatChange, formatValue, last, rangeChange, windowed } from '../derive'
import type { Strings } from '../i18n'
import { formatDate } from '../i18n'
import { Chart } from './Chart'

interface Props {
  series: Series
  lang: Lang
  t: Strings
  range: Range
  onOpen: (id: string) => void
}

export function Tile({ series: s, lang, t, range, onOpen }: Props) {
  const pts = windowed(s, range)
  const change = rangeChange(s, pts)
  return (
    <article className={`card tile tint-${s.group}`}>
      <h4><button className="tile-open" onClick={() => onOpen(s.id)}>{s.name[lang]}</button></h4>
      <p className="sub">{s.sub[lang]}</p>
      <p className="val">
        <span className="num">{formatValue(s, last(s)[1])}</span>
        <span className={`pill ${direction(change)}`}>{formatChange(change)}</span>
      </p>
      <Chart points={pts} width={300} height={70} stepped={s.frequency === 'event'} />
      <p className="foot">{t.asOf} {formatDate(last(s)[0], lang)} · {range}</p>
    </article>
  )
}
