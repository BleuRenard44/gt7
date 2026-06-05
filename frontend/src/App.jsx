import { Activity, Flag, Gauge, RadioTower, Users } from 'lucide-react'
import { useRaceState } from './hooks/useRaceState'
import CircuitMap from './components/CircuitMap'
import Scoreboard from './components/Scoreboard'
import CarDetails from './components/CarDetails'
import TeamManager from './components/TeamManager'

export default function App() {
  const race = useRaceState()
  const { state, connected, error } = race
  const connectedCars = (state.telemetry || []).filter((car) => car.connected).length

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <div className="eyebrow">GT7 LAN Race Control</div>
          <h1>Dashboard course temps réel</h1>
        </div>

        <div className="statusPill">
          <RadioTower size={18} />
          <span className={connected ? 'ok' : 'ko'}>{connected ? 'WebSocket connecté' : 'Déconnecté'}</span>
        </div>
      </header>

      {error && <div className="error">{error}</div>}

      <section className="metrics">
        <Metric icon={<Users />} label="Équipes" value={state.teams.length} />
        <Metric icon={<Activity />} label="Consoles live" value={`${connectedCars}/${state.telemetry.length}`} />
        <Metric icon={<Flag />} label="Circuit" value={state.telemetry[0]?.track_name || 'N/A'} />
        <Metric icon={<Gauge />} label="Source" value="GT7 UDP" />
      </section>

      <main className="grid">
        <section className="panel mapPanel">
          <h2>Carte circuit</h2>
          <CircuitMap state={state} />
        </section>

        <section className="panel">
          <h2>Scoreboard</h2>
          <Scoreboard state={state} />
        </section>

        <section className="panel full">
          <h2>Voitures en direct</h2>
          <CarDetails state={state} />
        </section>

        <section className="panel full">
          <h2>Gestion équipes, pilotes et relais</h2>
          <TeamManager race={race} />
        </section>
      </main>
    </div>
  )
}

function Metric({ icon, label, value }) {
  return (
    <div className="metric">
      <div className="metricIcon">{icon}</div>
      <div>
        <div className="metricLabel">{label}</div>
        <div className="metricValue">{value}</div>
      </div>
    </div>
  )
}
