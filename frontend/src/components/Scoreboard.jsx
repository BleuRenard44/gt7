export default function Scoreboard({ state }) {
  const teamsById = new Map((state.teams || []).map((team) => [team.id, team]))
  const rows = [...(state.telemetry || [])].sort((a, b) => {
    if ((a.position || 999) !== (b.position || 999)) return (a.position || 999) - (b.position || 999)
    return (b.lap || 0) - (a.lap || 0) || (b.lap_progress || 0) - (a.lap_progress || 0)
  })

  return (
    <div className="tableWrap">
      <table>
        <thead>
          <tr>
            <th>Pos</th>
            <th>Équipe</th>
            <th>Console</th>
            <th>Tour</th>
            <th>Progression</th>
            <th>Vitesse</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((car, index) => {
            const team = teamsById.get(car.team_id)
            return (
              <tr key={car.console_ip}>
                <td>#{car.position || index + 1}</td>
                <td>
                  <span className="teamSwatch" style={{ background: team?.color || '#64748b' }} />
                  {team?.name || 'Non assigné'}
                </td>
                <td>{car.console_ip}</td>
                <td>{car.lap}</td>
                <td>{Math.round((car.lap_progress || 0) * 100)}%</td>
                <td>{Math.round(car.speed_kph)} km/h</td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
