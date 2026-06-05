export default function CarDetails({ state }) {
  const teamsById = new Map((state.teams || []).map((team) => [team.id, team]))

  return (
    <div className="cards">
      {(state.telemetry || []).map((car) => {
        const team = teamsById.get(car.team_id)
        const pilot = team?.pilots?.find((item) => item.id === car.pilot_id)
        const key = car.source_id || `${car.worker_id}:${car.console_ip}`

        return (
          <article className="carCard" key={key}>
            <div className="carHeader">
              <span className="teamSwatch big" style={{ background: team?.color || '#64748b' }} />
              <div>
                <h3>{team?.name || car.console_ip}</h3>
                <p>{key} · {pilot?.name || 'Aucun pilote actif'}</p>
              </div>
            </div>

            <div className="carStats">
              <Stat label="Connectée" value={car.connected ? 'Oui' : 'Non'} />
              <Stat label="Paquet" value={car.packet_id ?? 'N/A'} />
              <Stat label="Vitesse" value={`${Math.round(car.speed_kph || 0)} km/h`} />
              <Stat label="RPM" value={Math.round(car.rpm || 0)} />
              <Stat label="Rapport" value={car.gear || 'N'} />
              <Stat label="Suggéré" value={car.suggested_gear ?? 'N/A'} />
              <Stat label="Throttle" value={`${Math.round((car.throttle || 0) * 100)}%`} />
              <Stat label="Brake" value={`${Math.round((car.brake || 0) * 100)}%`} />
              <Stat label="Essence" value={car.fuel_liters == null ? 'N/A' : `${car.fuel_liters} L`} />
              <Stat label="Pneu FL" value={fmt(car.tire_fl)} />
              <Stat label="Pneu FR" value={fmt(car.tire_fr)} />
              <Stat label="Pneu RL" value={fmt(car.tire_rl)} />
              <Stat label="Pneu RR" value={fmt(car.tire_rr)} />
              <Stat label="X monde" value={fmt(car.world_x)} />
              <Stat label="Z monde" value={fmt(car.world_z)} />
              <Stat label="Distance circuit" value={car.distance_to_track == null ? '—' : fmt(car.distance_to_track)} />
            </div>
          </article>
        )
      })}
    </div>
  )
}

function Stat({ label, value }) {
  return <div className="stat"><span>{label}</span><strong>{value}</strong></div>
}

function fmt(value) {
  if (value == null) return 'N/A'
  return typeof value === 'number' ? Math.round(value * 100) / 100 : value
}
