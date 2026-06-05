import { fmt } from '../utils'

export default function PerformancePanel({ state }) {
  const teamsBySource = new Map((state.teams || []).map((team) => [team.source_id, team]))
  const rows = [...(state.performance || [])].sort((a, b) => {
    if (a.delta_to_leader == null) return 1
    if (b.delta_to_leader == null) return -1
    return a.delta_to_leader - b.delta_to_leader
  })

  return (
    <div className="tableWrap">
      <table>
        <thead>
          <tr>
            <th>Équipe</th>
            <th>Best lap</th>
            <th>Last lap</th>
            <th>Best S1</th>
            <th>Best S2</th>
            <th>Best S3</th>
            <th>Δ leader</th>
            <th>Δ ahead</th>
            <th>Pneus</th>
            <th>Restant</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((p) => {
            const team = teamsBySource.get(p.source_id)
            return (
              <tr key={p.source_id}>
                <td><span className="teamSwatch" style={{ background: team?.color || '#64748b' }} />{team?.name || p.source_id}</td>
                <td>{time(p.best_lap_time)}</td>
                <td>{time(p.last_lap_time)}</td>
                <td>{time(p.best_sector_1)}</td>
                <td>{time(p.best_sector_2)}</td>
                <td>{time(p.best_sector_3)}</td>
                <td>{delta(p.delta_to_leader)}</td>
                <td>{delta(p.delta_to_ahead)}</td>
                <td><span className={`tyreBadge ${p.tyre_status}`}>{fmt(p.tyre_avg, 1)}</span></td>
                <td>{p.tyre_laps_remaining == null ? '—' : `${fmt(p.tyre_laps_remaining, 1)} tours`}</td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

function time(value) {
  if (value == null) return '—'
  const m = Math.floor(value / 60)
  const s = value - m * 60
  return `${m}:${s.toFixed(3).padStart(6, '0')}`
}

function delta(value) {
  if (value == null) return '—'
  if (Math.abs(value) < 0.001) return 'Leader'
  return `+${value.toFixed(3)}`
}
