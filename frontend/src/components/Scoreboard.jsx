export default function Scoreboard({ state }) {
  const teamsById = new Map((state.teams || []).map((team) => [team.id, team]))
  const rows = [...(state.telemetry || [])].sort((a, b) => {
    if (!!b.connected !== !!a.connected) return Number(b.connected) - Number(a.connected)
    return (a.position || 999) - (b.position || 999)
  })

  return (
    <div className="tableWrap">
      <table>
        <thead>
          <tr>
            <th>Live</th>
            <th>Pos</th>
            <th>Équipe</th>
            <th>Console</th>
            <th>Tour</th>
            <th>Vitesse</th>
            <th>RPM</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((car, index) => {
            const team = teamsById.get(car.team_id)
            return (
              <tr key={car.console_ip}>
                <td><span className={car.connected ? 'liveDot on' : 'liveDot'} /></td>
                <td>#{car.position || index + 1}</td>
                <td><span className="teamSwatch" style={{ background: team?.color || '#64748b' }} />{team?.name || 'Non assigné'}</td>
                <td>{car.console_ip}</td>
                <td>{car.lap}</td>
                <td>{Math.round(car.speed_kph || 0)} km/h</td>
                <td>{Math.round(car.rpm || 0)}</td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
