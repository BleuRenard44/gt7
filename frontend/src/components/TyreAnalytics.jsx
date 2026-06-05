import GaugeBar from './GaugeBar'
import { fmt, sourceKey, teamBySource } from '../utils'

export default function TyreAnalytics({ state }) {
  const perfBySource = new Map((state.performance || []).map((p) => [p.source_id, p]))
  return (
    <div className="tyreGrid">
      {(state.telemetry || []).map((car) => {
        const key = sourceKey(car)
        const team = teamBySource(state, key)
        const perf = perfBySource.get(key)
        return (
          <article className="tyreCard" key={key}>
            <header>
              <span className="teamSwatch big" style={{ background: team?.color || '#64748b' }} />
              <div>
                <h3>{team?.name || key}</h3>
                <p>{perf?.tyre_status || 'unknown'} · usure/tour {fmt(perf?.tyre_wear_per_lap, 3)}</p>
              </div>
            </header>
            <div className="tyreBars">
              <GaugeBar label="FL" value={car.tire_fl} />
              <GaugeBar label="FR" value={car.tire_fr} />
              <GaugeBar label="RL" value={car.tire_rl} />
              <GaugeBar label="RR" value={car.tire_rr} />
            </div>
            <div className={`tyrePrediction ${perf?.tyre_status || 'unknown'}`}>
              Restant estimé : {perf?.tyre_laps_remaining == null ? '—' : `${fmt(perf.tyre_laps_remaining, 1)} tours`}
            </div>
          </article>
        )
      })}
    </div>
  )
}
