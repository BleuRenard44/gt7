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
                <p>{pilot?.name || 'Aucun pilote actif'} · {pilot?.car || `Car ID ${car.car_id || 'N/A'}`}</p>
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
              <Stat label="Capacité" value={car.fuel_capacity_liters == null ? 'N/A' : `${car.fuel_capacity_liters} L`} />
              <Stat label="Pneu FL" value={formatValue(car.tire_fl)} />
              <Stat label="Pneu FR" value={formatValue(car.tire_fr)} />
              <Stat label="Pneu RL" value={formatValue(car.tire_rl)} />
              <Stat label="Pneu RR" value={formatValue(car.tire_rr)} />
              <Stat label="Oil temp" value={formatValue(car.oil_temp)} />
              <Stat label="Water temp" value={formatValue(car.water_temp)} />
              <Stat label="X monde" value={formatValue(car.world_x)} />
              <Stat label="Z monde" value={formatValue(car.world_z)} />
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

function formatValue(value) {
  if (value == null) return 'N/A'
  if (typeof value === 'number') return Math.round(value * 100) / 100
  return value
}
