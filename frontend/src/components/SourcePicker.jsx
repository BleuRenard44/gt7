import { sourceKey, teamBySource } from '../utils'

export default function SourcePicker({ state, selectedSource, setSelectedSource }) {
  const sources = (state.telemetry || []).map(sourceKey)
  return (
    <div className="sourcePicker">
      {sources.map((source) => {
        const team = teamBySource(state, source)
        return (
          <button key={source} className={selectedSource === source ? 'sourceCard active' : 'sourceCard'} onClick={() => setSelectedSource(source)}>
            <span className="teamSwatch big" style={{ background: team?.color || '#64748b' }} />
            <strong>{team?.name || source}</strong>
            <small>{source}</small>
          </button>
        )
      })}
    </div>
  )
}
