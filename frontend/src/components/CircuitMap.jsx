export default function CircuitMap({ state }) {
  const telemetry = state.telemetry || []
  const teamsByIp = new Map((state.teams || []).map((team) => [team.console_ip, team]))

  const path = 'M 90 250 C 100 80, 260 50, 430 100 C 570 145, 710 60, 810 160 C 920 270, 810 430, 610 410 C 430 395, 410 515, 250 455 C 120 405, 70 330, 90 250 Z'

  return (
    <div className="trackWrap">
      <svg viewBox="0 0 1000 560" className="trackSvg" role="img" aria-label="Carte du circuit">
        <rect x="0" y="0" width="1000" height="560" rx="28" className="trackBg" />
        <path d={path} className="trackOuter" />
        <path d={path} className="trackInner" />
        <line x1="82" y1="220" x2="142" y2="235" className="startLine" />

        {telemetry.map((car) => {
          const team = teamsByIp.get(car.console_ip)
          const x = car.x * 1000
          const y = car.y * 560
          return (
            <g key={car.console_ip} transform={`translate(${x} ${y})`}>
              <circle r="16" fill={team?.color || '#f8fafc'} className="carDot" />
              <circle r="6" fill="#020617" />
              <text x="22" y="5" className="carLabel">
                {team?.name || car.console_ip}
              </text>
            </g>
          )
        })}
      </svg>
    </div>
  )
}
