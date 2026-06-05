export default function Scoreboard({ state, selectedSource, setSelectedSource }) {
  const teamsById = new Map((state.teams || []).map((team) => [team.id, team]))
  const rows = [...(state.telemetry || [])].sort((a, b) => {
    if (!!b.connected !== !!a.connected) return Number(b.connected) - Number(a.connected)
    if ((a.position || 999) !== (b.position || 999)) return (a.position || 999) - (b.position || 999)
    return (b.track_progress || 0) - (a.track_progress || 0)
  })

  return (
    <div className="tableWrap">
      <table>
        <thead>
          <tr>
            <th>Live</th>
            <th>Pos</th>
            <th>Équipe</th>
            <th>Source</th>
            <th>Tour</th>
            <th>Prog.</th>
            <th>Vitesse</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((car, index) => {
            const team = teamsById.get(car.team_id)
            const key = car.source_id || `${car.worker_id}:${car.console_ip}`
            return (
              <tr key={key} className={selectedSource === key ? 'selectedRow' : ''} onClick={() => setSelectedSource?.(key)}>
                <td><span className={car.connected ? 'liveDot on' : 'liveDot'} /></td>
                <td>#{car.position || index + 1}</td>
                <td><span className="teamSwatch" style={{ background: team?.color || '#64748b' }} />{team?.name || 'Non assigné'}</td>
                <td><span className="mono">{key}</span></td>
                <td>{car.lap}</td>
                <td>{car.track_progress == null ? '—' : `${Math.round(car.track_progress * 100)}%`}</td>
                <td>{Math.round(car.speed_kph || 0)} km/h</td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
