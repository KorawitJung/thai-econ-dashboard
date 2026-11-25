import type { Point } from '../data'
import { geometry } from '../derive'

export function Sparkline({ points, stepped, tone }: { points: Point[]; stepped: boolean; tone: string }) {
  const g = geometry(points, 64, 30, 2, stepped)
  return (
    <svg className="spark" width="64" height="30" viewBox="0 0 64 30" aria-hidden="true">
      <polyline points={g.line} className={`stroke-${tone}`} />
    </svg>
  )
}
