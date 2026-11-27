import { useCallback, useEffect, useState } from 'react'
import { Chips } from './components/Chips'
import { Detail } from './components/Detail'
import { Summary } from './components/Summary'
import { Tile } from './components/Tile'
import type { Theme } from './components/TopBar'
import { TopBar } from './components/TopBar'
import type { Dashboard, Lang } from './data'
import { parseDashboard } from './data'
import type { Range } from './derive'
import { filterSeries } from './derive'
import { STRINGS, formatDateTime } from './i18n'

type Load =
  | { status: 'loading' }
  | { status: 'error'; message: string }
  | { status: 'ready'; data: Dashboard }

const DATA_URL = `${import.meta.env.BASE_URL}data/dashboard.json`

function storedLang(): Lang {
  try {
    const v = localStorage.getItem('lang')
    if (v === 'th' || v === 'en') return v
  } catch {
    // Storage can be blocked; Thai is the default.
  }
  return 'th'
}

function storedTheme(): Theme {
  try {
    const v = localStorage.getItem('theme')
    if (v === 'light' || v === 'dark') return v
  } catch {
    // Storage can be blocked; follow the device.
  }
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

const selectedFromHash = () => decodeURIComponent(location.hash.slice(1))

export function App() {
  const [load, setLoad] = useState<Load>({ status: 'loading' })
  const [lang, setLang] = useState<Lang>(storedLang)
  const [theme, setTheme] = useState<Theme>(storedTheme)
  const [range, setRange] = useState<Range>('1Y')
  const [group, setGroup] = useState('all')
  const [query, setQuery] = useState('')
  const [selected, setSelected] = useState(selectedFromHash)
  const t = STRINGS[lang]

  const fetchData = useCallback(() => {
    setLoad({ status: 'loading' })
    fetch(DATA_URL, { cache: 'no-cache' })
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`)
        return r.json()
      })
      .then((json) => setLoad({ status: 'ready', data: parseDashboard(json) }))
      .catch((e: unknown) => setLoad({ status: 'error', message: e instanceof Error ? e.message : String(e) }))
  }, [])

  useEffect(fetchData, [fetchData])

  useEffect(() => {
    const onHash = () => setSelected(selectedFromHash())
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && location.hash) location.hash = ''
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [])

  useEffect(() => {
    document.documentElement.lang = lang
    document.title = t.title
    try {
      localStorage.setItem('lang', lang)
    } catch {
      // Not remembering the choice is fine.
    }
  }, [lang, t.title])

  useEffect(() => {
    document.documentElement.dataset.theme = theme
    try {
      localStorage.setItem('theme', theme)
    } catch {
      // Not remembering the choice is fine.
    }
  }, [theme])

  const bar = (
    <TopBar t={t} lang={lang} generated={load.status === 'ready' ? load.data.generated : ''}
      range={range} onRange={setRange} query={query} onQuery={setQuery}
      theme={theme} onTheme={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
      onLang={() => setLang(lang === 'th' ? 'en' : 'th')} onRefresh={fetchData} />
  )

  if (load.status !== 'ready') {
    return (
      <>
        {bar}
        <main className="page state" role={load.status === 'error' ? 'alert' : undefined}>
          <p>{load.status === 'error' ? t.failed : t.loading}</p>
          {load.status === 'error' && <p className="muted">{load.message}</p>}
          {load.status === 'error' && <button className="chip" onClick={fetchData}>{t.retry}</button>}
        </main>
      </>
    )
  }

  const data = load.data
  const shown = filterSeries(data.series, group, query)
  const groups = data.groups.filter((g) => shown.some((s) => s.group === g.id))
  const open = (id: string) => { location.hash = id === selected ? '' : id }

  return (
    <>
      {bar}
      <main className="page">
        <Summary lines={data.summary} t={t} />
        <div className="page-head">
          <h2 className="section-title">{t.indicators}</h2>
          {data.source === 'sample'
            ? <span className="status sample" role="note">{t.sample}</span>
            : <span className="status"><span className="dot" aria-hidden="true" />{t.updated} {formatDateTime(data.generated, lang)}</span>}
        </div>
        <Chips groups={data.groups} series={data.series} group={group} onGroup={setGroup} lang={lang} t={t} />
        {groups.length === 0 && <p className="muted">{t.none}</p>}
        {groups.map((g) => (
          <section key={g.id} aria-labelledby={`group-${g.id}`}>
            <div className="group-head"><h3 id={`group-${g.id}`}>{g.name[lang]}</h3></div>
            <div className="grid">
              {shown.filter((s) => s.group === g.id).map((s) => (
                s.id === selected
                  ? (
                    <div className="span-all" key={s.id}>
                      <Detail key={s.id} data={data} series={s} lang={lang} t={t} range={range}
                        onClose={() => { location.hash = '' }} />
                    </div>
                  )
                  : <Tile key={s.id} series={s} lang={lang} t={t} range={range} onOpen={open} />
              ))}
            </div>
          </section>
        ))}
        <p className="footnote">{t.disclaimer}</p>
      </main>
    </>
  )
}
