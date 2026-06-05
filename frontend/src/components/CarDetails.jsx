export default function CarDetails({ state }) {
  const teamsById = new Map((state.teams || []).map((team) => [team.id, team]))

  return (
    <div className="cards">
      {(state.telemetry || []).map((car) => {
        const team = teamsById.get(car.team_id)
        const pilot = team?.pilots?.find((item) => item.id === car.pilot_id)

        return (
          <article className="carCard" key={car.console_ip}>
            <div className="carHeader">
              <span className="teamSwatch big" style={{ background: team?.color || '#64748b' }} />
              <div>
                <h3>{team?.name || car.console_ip}</h3>
                <p>{pilot?.name || 'Aucun pilote actif'} · {pilot?.car || 'Voiture non renseignée'}</p>
              </div>
            </div>

            <div className="carStats">
              <Stat label="Vitesse" value={`${Math.round(car.speed_kph)} km/h`} />
              <Stat label="RPM" value={car.rpm} />
              <Stat label="Rapport" value={car.gear > 0 ? car.gear : 'N'} />
              <Stat label="Essence" value={car.fuel_liters == null ? 'N/A' : `${car.fuel_liters} L`} />
              <Stat label="Throttle" value={`${Math.round((car.throttle || 0) * 100)}%`} />
              <Stat label="Brake" value={`${Math.round((car.brake || 0) * 100)}%`} />
              <Stat label="Pneu FL" value={formatPercent(car.tire_fl)} />
              <Stat label="Pneu FR" value={formatPercent(car.tire_fr)} />
              <Stat label="Pneu RL" value={formatPercent(car.tire_rl)} />
              <Stat label="Pneu RR" value={formatPercent(car.tire_rr)} />
              <Stat label="Moteur" value={formatPercent(car.damage_engine)} />
              <Stat label="Carrosserie" value={formatPercent(car.damage_body)} />
            </div>
          </article>
        )
      })}
    </div>
  )
}

function Stat({ label, value }) {
  return (
    <div className="stat">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  )
}

function formatPercent(value) {
  if (value == null) return 'N/A'
  return `${Math.round(value)}%`
}
