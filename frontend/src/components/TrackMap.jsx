import { useMemo, useState } from 'react'
import HeatmapOverlay from './HeatmapOverlay'

export default function TrackMap({
  state,
  selectedSource,
  setSelectedSource,
  showControls = true,
  defaultHeatmap = true
}) {
  const [showHeatmap, setShowHeatmap] = useState(defaultHeatmap)
  const [heatmapMode, setHeatmapMode] = useState('all')
  const [thinTrack, setThinTrack] = useState(true)

  const track = state.active_track
  const teamsById = new Map((state.teams || []).map((team) => [team.id, team]))

  const trackPath = useMemo(() => buildPath(track?.points || []), [track])
  const fallbackPath =
    'M 90 250 C 100 80, 260 50, 430 100 C 570 145, 710 60, 810 160 C 920 270, 810 430, 610 410 C 430 395, 410 515, 250 455 C 120 405, 70 330, 90 250 Z'

  return (
    <div className="trackWrap">
      {showControls && (
        <div className="trackToolbar">
          <div className="trackToolbarGroup">
            <button
              className={showHeatmap ? 'activeBtn' : 'secondary'}
              onClick={() => setShowHeatmap((value) => !value)}
            >
              {showHeatmap ? 'Heatmap ON' : 'Heatmap OFF'}
            </button>

            <select
              value={heatmapMode}
              onChange={(event) => {
                setHeatmapMode(event.target.value)
                setShowHeatmap(true)
              }}
              disabled={!showHeatmap}
            >
              <option value="all">Toutes zones</option>
              <option value="brake">Freinage</option>
              <option value="throttle">Accélération</option>
              <option value="coast">Coast</option>
            </select>
          </div>

          <button
            className={thinTrack ? 'activeBtn' : 'secondary'}
            onClick={() => setThinTrack((value) => !value)}
          >
            {thinTrack ? 'Circuit fin' : 'Circuit large'}
          </button>
        </div>
      )}

      <svg viewBox="0 0 1000 620" className={thinTrack ? 'trackSvg thinTrack' : 'trackSvg'}>
        <defs>
          <filter id="glow">
            <feGaussianBlur stdDeviation="4" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>

        <rect x="0" y="0" width="1000" height="620" rx="28" className="trackBg" />

        {track && track.points.length > 1 ? (
          <>
            <path d={trackPath} className="trackOuter auto" />
            <path d={trackPath} className="trackInner auto" />
            <circle
              cx={track.points[0].nx * 1000}
              cy={track.points[0].ny * 620}
              r={thinTrack ? 5 : 9}
              className="startMarker"
            />
          </>
        ) : (
          <>
            <path d={fallbackPath} className="trackOuter" />
            <path d={fallbackPath} className="trackInner" />
            <line x1="82" y1="220" x2="142" y2="235" className="startLine" />
          </>
        )}

        {showHeatmap && <HeatmapOverlay state={state} mode={heatmapMode} />}

        {(state.telemetry || []).map((car) => {
          const team = teamsById.get(car.team_id)
          const x = clamp(car.x ?? 0.5, 0.02, 0.98) * 1000
          const y = clamp(car.y ?? 0.5, 0.02, 0.98) * 620
          const key = car.source_id || `${car.worker_id}:${car.console_ip}`
          const rotation = Math.round((car.track_progress || 0) * 360)

          return (
            <g
              key={key}
              transform={`translate(${x} ${y})`}
              opacity={car.connected ? 1 : 0.32}
              onClick={() => setSelectedSource?.(key)}
              className={selectedSource === key ? 'selectedCarGroup' : ''}
            >
              <circle r={thinTrack ? 10 : 20} fill={team?.color || '#f8fafc'} className="carHalo" filter="url(#glow)" />
              <g transform={`rotate(${rotation})`}>
                <path
                  d={thinTrack ? 'M 0 -10 L 7 8 L 0 5 L -7 8 Z' : 'M 0 -17 L 12 14 L 0 8 L -12 14 Z'}
                  fill={team?.color || '#f8fafc'}
                  stroke="#fff"
                  strokeWidth={thinTrack ? '1.2' : '2'}
                />
              </g>
              <text x={thinTrack ? 16 : 26} y="6" className="carLabel">
                {team?.name || car.console_ip}
              </text>
            </g>
          )
        })}
      </svg>

      {!track && <p className="hint">Aucun circuit enregistré. Utilise le bouton d'enregistrement du circuit.</p>}
    </div>
  )
}

function buildPath(points) {
  if (!points.length) return ''
  const [first, ...rest] = points
  return `M ${first.nx * 1000} ${first.ny * 620} ` + rest.map((p) => `L ${p.nx * 1000} ${p.ny * 620}`).join(' ')
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value))
}
