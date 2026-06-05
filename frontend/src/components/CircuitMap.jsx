export default function CircuitMap({ state }) {
  const teamsById = new Map((state.teams || []).map((team) => [team.id, team]))
  const path = 'M 90 250 C 100 80, 260 50, 430 100 C 570 145, 710 60, 810 160 C 920 270, 810 430, 610 410 C 430 395, 410 515, 250 455 C 120 405, 70 330, 90 250 Z'

  return (
    <div className="trackWrap">
      <svg viewBox="0 0 1000 560" className="trackSvg">
        <rect x="0" y="0" width="1000" height="560" rx="28" className="trackBg" />
        <path d={path} className="trackOuter" />
        <path d={path} className="trackInner" />
        <line x1="82" y1="220" x2="142" y2="235" className="startLine" />
        {(state.telemetry || []).map((car) => {
          const team = teamsById.get(car.team_id)
          const x = (car.x || 0.5) * 1000
          const y = (car.y || 0.5) * 560
          return (
            <g key={car.source_id || `${car.worker_id}:${car.console_ip}`} transform={`translate(${x} ${y})`} opacity={car.connected ? 1 : 0.35}>
              <circle r="17" fill={team?.color || '#f8fafc'} className="carDot" />
              <circle r="6" fill="#020617" />
              <text x="24" y="6" className="carLabel">{team?.name || car.console_ip}</text>
            </g>
          )
        })}
      </svg>
      <p className="hint">Chaque source = worker_id + console_ip. Plusieurs workers et plusieurs consoles sont supportés.</p>
    </div>
  )
}
