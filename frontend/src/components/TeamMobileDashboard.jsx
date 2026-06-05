import CompleteCarInfo from './CompleteCarInfo'
import GaugeBar from './GaugeBar'
import { activePilot, carBySource, fmt, sourceKey, teamBySource } from '../utils'
import { api } from '../api'

export default function TeamMobileDashboard({ race, sourceId }) {
  const { state, refresh } = race
  const source = sourceId || sourceKey((state.telemetry || [])[0])
  const car = carBySource(state, source)
  const team = teamBySource(state, source)
  const pilot = activePilot(team)
  const relays = team?.relay_order || []
  const penalties = (state.penalties || []).filter((p) => p.source_id === source && !p.served)
  const pits = (state.pit_stops || []).filter((p) => p.source_id === source && !p.ended_at)

  async function nextRelay() {
    if (!team) return
    await api.startNextRelay(team.id)
    await refresh()
  }

  if (!source || !team) return <section className="panel phoneFrame"><div className="empty">Sélectionne une équipe.</div></section>

  return (
    <section className="phoneFrame">
      <div className={`phoneFlag ${state.session?.flag || 'green'}`}>{state.session?.flag || 'green'}</div>

      <div className="phoneHeader">
        <span className="teamSwatch mega" style={{ background: team.color }} />
        <div>
          <h2>{team.name}</h2>
          <p>{pilot?.name || 'Aucun pilote actif'}</p>
        </div>
      </div>

      <div className="phoneSpeed">
        <strong>{fmt(car?.speed_kph, 0)}</strong>
        <span>km/h</span>
      </div>

      <div className="phoneVitals">
        <GaugeBar label="Throttle" value={(car?.throttle || 0) * 100} suffix="%" />
        <GaugeBar label="Brake" value={(car?.brake || 0) * 100} suffix="%" reverse />
        <GaugeBar label="Fuel" value={fuelPercent(car)} suffix="%" />
      </div>

      <div className="phoneGrid">
        <Tile label="Tour" value={car?.lap ?? '—'} />
        <Tile label="Pos" value={car?.position ?? '—'} />
        <Tile label="RPM" value={fmt(car?.rpm, 0)} />
        <Tile label="Gear" value={car?.gear || 'N'} />
      </div>

      <div className="phoneSection">
        <h3>Pneus</h3>
        <div className="phoneGrid">
          <Tile label="FL" value={fmt(car?.tire_fl)} />
          <Tile label="FR" value={fmt(car?.tire_fr)} />
          <Tile label="RL" value={fmt(car?.tire_rl)} />
          <Tile label="RR" value={fmt(car?.tire_rr)} />
        </div>
      </div>

      <div className="phoneSection">
        <h3>Relais</h3>
        <button onClick={nextRelay}>Passer au relais suivant</button>
        <ol className="relayList mobile">
          {relays.map((relay) => {
            const p = team.pilots.find((pilot) => pilot.id === relay.pilot_id)
            return <li key={relay.id} className={relay.status}>{p?.name || 'Pilote supprimé'} · {relay.status}</li>
          })}
        </ol>
      </div>

      {(penalties.length > 0 || pits.length > 0) && (
        <div className="phoneAlerts">
          {penalties.map((p) => <div key={p.id}>Pénalité +{p.seconds}s · {p.reason}</div>)}
          {pits.map((p) => <div key={p.id}>Pit stop en cours</div>)}
        </div>
      )}

      <details>
        <summary>Infos voiture complètes</summary>
        <CompleteCarInfo state={state} sourceId={source} />
      </details>
    </section>
  )
}

function Tile({ label, value }) {
  return <div className="phoneTile"><span>{label}</span><strong>{value}</strong></div>
}

function fuelPercent(car) {
  if (!car?.fuel_capacity_liters) return null
  return (car.fuel_liters / car.fuel_capacity_liters) * 100
}
