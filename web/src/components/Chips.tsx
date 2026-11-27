import type { Group, Lang, Series } from '../data'
import type { Strings } from '../i18n'

interface Props {
  groups: Group[]
  /** Every indicator, not the filtered ones, so a chip counts what picking it would show. */
  series: Series[]
  group: string
  onGroup: (g: string) => void
  lang: Lang
  t: Strings
}

export function Chips({ groups, series, group, onGroup, lang, t }: Props) {
  const count = (id: string) => series.filter((s) => id === 'all' || s.group === id).length
  return (
    <div className="chips" role="group" aria-label={t.groupLabel}>
      <button className="chip" aria-pressed={group === 'all'} onClick={() => onGroup('all')}>
        {t.all}<span className="count">{count('all')}</span>
      </button>
      {groups.map((g) => (
        <button key={g.id} className={`chip tint-${g.id}`} aria-pressed={group === g.id} onClick={() => onGroup(g.id)}>
          <span className="dot" aria-hidden="true" />{g.name[lang]}<span className="count">{count(g.id)}</span>
        </button>
      ))}
    </div>
  )
}
