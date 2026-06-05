export default function HeatmapOverlay({ state, mode = 'all' }) {
  const points = (state.heatmap || [])
    .filter((p) => mode === 'all' || p.kind === mode)
    .slice(-900)

  return (
    <g className="heatmapLayer">
      {points.map((p, index) => {
        const intensity = Math.max(0.05, Math.min(1, p.intensity || 0.2))
        return (
          <circle
            key={`${p.source_id}-${p.timestamp}-${index}`}
            cx={(p.x || 0.5) * 1000}
            cy={(p.y || 0.5) * 620}
            r={2.5 + intensity * 8}
            className={`heatPoint ${p.kind}`}
            opacity={0.04 + intensity * 0.22}
          />
        )
      })}
    </g>
  )
}
