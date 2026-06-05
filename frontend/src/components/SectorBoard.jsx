import { fmt } from '../utils'

export default function SectorBoard({ state }) {
  const teamsBySource = new Map((state.teams || []).map((team) => [team.source_id, team]))
  const recent = [...(state.sectors || [])].reverse().slice(0, 60)

  return (
    <div className="sectorBoard">
      {recent.map((s) => {
        const team = teamsBySource.get(s.source_id)
        return (
          <div className="sectorItem" key={s.id}>
            <span className="teamSwatch" style={{ background: team?.color || '#64748b' }} />
            <strong>{team?.name || s.source_id}</strong>
            <span>Tour {s.lap}</span>
            <span>{s.sector_name}</span>
            <b>{formatSector(s.sector_time)}</b>
          </div>
        )
      })}
    </div>
  )
}

function formatSector(value) {
  if (value == null) return '—'
  return `${fmt(value, 3)}s`
}
