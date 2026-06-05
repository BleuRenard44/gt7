import { Battery, Disc3, Fuel, Gauge, MapPin, Thermometer, Timer, Wrench } from 'lucide-react'
import GaugeBar from './GaugeBar'
import { activePilot, carBySource, fmt, sourceKey, teamBySource } from '../utils'

export default function CompleteCarInfo({ state, sourceId }) {
  const source = sourceId || sourceKey((state.telemetry || [])[0])
  const car = carBySource(state, source)
  const team = teamBySource(state, source)
  const perfBySource = new Map((state.performance || []).map((p) => [p.source_id, p]))
  const perf = perfBySource.get(source)
  const pilot = activePilot(team)

  if (!car) {
    return <div className="empty">Aucune voiture sélectionnée.</div>
  }

  const tyreAvg = avg([car.tire_fl, car.tire_fr, car.tire_rl, car.tire_rr])
  const fuelRatio = car.fuel_capacity_liters ? (car.fuel_liters / car.fuel_capacity_liters) * 100 : null

  return (
    <div className="completeCar">
      <header className="carHero">
        <div className="carHeroIdentity">
          <span className="teamSwatch mega" style={{ background: team?.color || '#64748b' }} />
          <div>
            <h2>{team?.name || source}</h2>
            <p>{pilot?.name || 'Pilote non assigné'} · {pilot?.car || `Car ID ${car.car_id || 'N/A'}`}</p>
            <small>{source}</small>
          </div>
        </div>
        <div className="speedHero">
          <strong>{fmt(car.speed_kph, 0)}</strong>
          <span>km/h</span>
        </div>
      </header>

      <section className="carDashGrid">
        <BigTile icon={<Gauge />} label="RPM" value={fmt(car.rpm, 0)} sub={`Gear ${car.gear || 'N'} · suggéré ${car.suggested_gear ?? '—'}`} />
        <BigTile icon={<Fuel />} label="Fuel" value={car.fuel_liters == null ? '—' : `${fmt(car.fuel_liters, 1)} L`} sub={fuelRatio == null ? 'Capacité inconnue' : `${fmt(fuelRatio, 0)}% restant`} />
        <BigTile icon={<Disc3 />} label="Tyres avg" value={tyreAvg == null ? '—' : fmt(tyreAvg, 1)} sub={`FL ${fmt(car.tire_fl)} · FR ${fmt(car.tire_fr)} · RL ${fmt(car.tire_rl)} · RR ${fmt(car.tire_rr)}`} />
        <BigTile icon={<Timer />} label="Delta leader" value={perf?.delta_to_leader == null ? '—' : `+${fmt(perf.delta_to_leader, 3)}s`} sub={perf?.delta_to_ahead == null ? 'No car ahead' : `ahead +${fmt(perf.delta_to_ahead, 3)}s`} />
        <BigTile icon={<MapPin />} label="Track progress" value={car.track_progress == null ? '—' : `${fmt(car.track_progress * 100, 0)}%`} sub={`distance ${fmt(car.distance_to_track, 1)}`} />
      </section>

      <section className="panelSub">
        <h3>Contrôles pilote</h3>
        <div className="gaugeGrid">
          <GaugeBar label="Throttle" value={(car.throttle || 0) * 100} suffix="%" />
          <GaugeBar label="Brake" value={(car.brake || 0) * 100} suffix="%" reverse />
          <GaugeBar label="Fuel" value={fuelRatio} suffix="%" />
          <GaugeBar label="Boost" value={(car.boost || 0) * 100} suffix="%" />
        </div>
      </section>

      <section className="panelSub">
        <h3>Chronos et secteurs</h3>
        <div className="statsGrid">
          <Stat label="Best lap" value={perf?.best_lap_time == null ? '—' : `${fmt(perf.best_lap_time, 3)}s`} />
          <Stat label="Last lap" value={perf?.last_lap_time == null ? '—' : `${fmt(perf.last_lap_time, 3)}s`} />
          <Stat label="Best S1" value={perf?.best_sector_1 == null ? '—' : `${fmt(perf.best_sector_1, 3)}s`} />
          <Stat label="Best S2" value={perf?.best_sector_2 == null ? '—' : `${fmt(perf.best_sector_2, 3)}s`} />
          <Stat label="Best S3" value={perf?.best_sector_3 == null ? '—' : `${fmt(perf.best_sector_3, 3)}s`} />
          <Stat label="Tyre wear/lap" value={fmt(perf?.tyre_wear_per_lap, 3)} />
          <Stat label="Tyre laps left" value={perf?.tyre_laps_remaining == null ? '—' : fmt(perf.tyre_laps_remaining, 1)} />
          <Stat label="Tyre status" value={perf?.tyre_status || 'unknown'} />
        </div>
      </section>

      <section className="panelSub">
        <h3>Pneus et roues</h3>
        <div className="statsGrid">
          <Stat label="Tire FL" value={fmt(car.tire_fl)} />
          <Stat label="Tire FR" value={fmt(car.tire_fr)} />
          <Stat label="Tire RL" value={fmt(car.tire_rl)} />
          <Stat label="Tire RR" value={fmt(car.tire_rr)} />
          <Stat label="Wheel speed FL" value={`${fmt(car.tire_speed_fl)} km/h`} />
          <Stat label="Wheel speed FR" value={`${fmt(car.tire_speed_fr)} km/h`} />
          <Stat label="Wheel speed RL" value={`${fmt(car.tire_speed_rl)} km/h`} />
          <Stat label="Wheel speed RR" value={`${fmt(car.tire_speed_rr)} km/h`} />
        </div>
      </section>

      <section className="panelSub">
        <h3>Températures et mécanique</h3>
        <div className="statsGrid">
          <Stat icon={<Thermometer />} label="Oil temp" value={`${fmt(car.oil_temp)} °C`} />
          <Stat icon={<Thermometer />} label="Water temp" value={`${fmt(car.water_temp)} °C`} />
          <Stat icon={<Wrench />} label="Oil pressure" value={fmt(car.oil_pressure, 3)} />
          <Stat icon={<Battery />} label="Ride height" value={`${fmt(car.ride_height_mm)} mm`} />
          <Stat icon={<Timer />} label="Lap" value={car.lap} />
          <Stat label="Position" value={car.position ?? '—'} />
          <Stat label="Total laps" value={car.total_laps ?? '—'} />
          <Stat label="Total cars" value={car.total_positions ?? '—'} />
        </div>
      </section>

      <section className="panelSub">
        <h3>Coordonnées brutes</h3>
        <div className="statsGrid">
          <Stat label="World X" value={fmt(car.world_x, 3)} />
          <Stat label="World Y" value={fmt(car.world_y, 3)} />
          <Stat label="World Z" value={fmt(car.world_z, 3)} />
          <Stat label="Packet ID" value={car.packet_id ?? '—'} />
          <Stat label="Connected" value={car.connected ? 'Oui' : 'Non'} />
          <Stat label="Timestamp" value={new Date((car.timestamp || 0) * 1000).toLocaleTimeString()} />
        </div>
      </section>
    </div>
  )
}

function BigTile({ icon, label, value, sub }) {
  return <div className="bigTile"><div className="bigIcon">{icon}</div><span>{label}</span><strong>{value}</strong><small>{sub}</small></div>
}

function Stat({ icon, label, value }) {
  return <div className="stat rich">{icon && <span className="statIcon">{icon}</span>}<span>{label}</span><strong>{value}</strong></div>
}

function avg(values) {
  const nums = values.filter((v) => typeof v === 'number')
  if (!nums.length) return null
  return nums.reduce((a, b) => a + b, 0) / nums.length
}
