import type { Point } from '../data'
import { geometry } from '../derive'

interface Props {
  points: Point[]
  /** Chart units. CSS sets the drawn size, so these only fix the shape of the curve. */
  width: number
  height: number
  stepped: boolean
  /** Given, the chart is announced instead of hidden. */
  label?: string
}

export function Chart({ points, width, height, stepped, label }: Props) {
  const g = geometry(points, width, height, 3, stepped)
  return (
    <svg className="chart" viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none"
      role={label ? 'img' : undefined} aria-label={label} aria-hidden={label ? undefined : true}>
      <polygon points={g.area} />
      <polyline points={g.line} />
    </svg>
  )
}
