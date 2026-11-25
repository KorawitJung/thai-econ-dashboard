import { useCallback, useEffect, useState } from 'react'
import { Detail } from './components/Detail'
import { Overview } from './components/Overview'
import type { Dashboard, Lang } from './data'
import { parseDashboard } from './data'
import type { Range } from './derive'
import { STRINGS } from './i18n'

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

const selectedFromHash = () => decodeURIComponent(location.hash.slice(1))

export function App() {
  const [load, setLoad] = useState<Load>({ status: 'loading' })
  const [lang, setLang] = useState<Lang>(storedLang)
  const [selected, setSelected] = useState(selectedFromHash)
  const [range, setRange] = useState<Range>('1Y')
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
    const onHash = () => {
      setSelected(selectedFromHash())
      window.scrollTo(0, 0)
    }
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
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

  const langButton = (
    <button className="lang" aria-label={t.langLabel} onClick={() => setLang(lang === 'th' ? 'en' : 'th')}>
      {t.langButton}
    </button>
  )

  if (load.status === 'loading') return <p className="state">{t.loading}</p>
  if (load.status === 'error') {
    return (
      <div className="state" role="alert">
        <p>{t.failed}</p>
        <p className="meta">{load.message}</p>
        <button className="lang" onClick={fetchData}>{t.retry}</button>
      </div>
    )
  }

  const series = load.data.series.find((s) => s.id === selected)
  if (selected && !series) {
    return (
      <div className="state" role="alert">
        <p>{t.notFound}</p>
        <a href="#">{t.back}</a>
      </div>
    )
  }
  return series ? (
    <Detail data={load.data} series={series} lang={lang} t={t} range={range} onRange={setRange}
      onBack={() => { location.hash = '' }} langButton={langButton} />
  ) : (
    <Overview data={load.data} lang={lang} t={t} onOpen={(id) => { location.hash = id }} langButton={langButton} />
  )
}
