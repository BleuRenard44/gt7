import { Gauge } from 'lucide-react'
import { fmt, sourceKey, teamBySource } from '../utils'

export default function MiniCarStrip({ state, selectedSource, setSelectedSource }) {
  return (
    <div className="miniCarStrip">
      {(state.telemetry || []).map((car) => {
        const key = sourceKey(car)
        const team = teamBySource(state, key)
        return (
          <button key={key} className={selectedSource === key ? 'miniCar active' : 'miniCar'} onClick={() => setSelectedSource(key)}>
            <span className="teamSwatch big" style={{ background: team?.color || '#64748b' }} />
            <span>
              <strong>{team?.name || key}</strong>
              <small>{fmt(car.speed_kph, 0)} km/h · {fmt(car.rpm, 0)} rpm · G{car.gear}</small>
            </span>
            <Gauge size={20} />
          </button>
        )
      })}
    </div>
  )
}
