import { useMemo, useState } from 'react'
import { Activity, Car, ClipboardList, Flag, LayoutDashboard, Map, Monitor, RadioTower, Smartphone, Users, Wrench, BarChart3 } from 'lucide-react'
import { useRaceState } from './hooks/useRaceState'
import RaceControlView from './views/RaceControlView'
import TeamsMobileView from './views/TeamsMobileView'
import CarDetailView from './views/CarDetailView'
import PerformanceView from './views/PerformanceView'
import PublicScreenView from './views/PublicScreenView'
import TrackView from './views/TrackView'
import ToolsView from './views/ToolsView'
import EventsView from './views/EventsView'
import { sourceKey } from './utils'

const views = [
  { id: 'control', label: 'Race Control', icon: LayoutDashboard },
  { id: 'teams', label: 'Teams Mobile', icon: Smartphone },
  { id: 'cars', label: 'Car Detail', icon: Car },
  { id: 'performance', label: 'Performance', icon: BarChart3 },
  { id: 'public', label: 'Public Screen', icon: Monitor },
  { id: 'tracks', label: 'Tracks', icon: Map },
  { id: 'tools', label: 'Tools', icon: Wrench },
  { id: 'events', label: 'Events', icon: ClipboardList }
]

export default function App() {
  const race = useRaceState()
  const { state, connected, error } = race
  const [view, setView] = useState(resolveInitialView())
  const [selectedSource, setSelectedSource] = useState(resolveInitialSource())

  const live = (state.telemetry || []).filter((car) => car.connected).length
  const workers = new Set((state.telemetry || []).map((car) => car.worker_id)).size
  const currentView = views.find((item) => item.id === view) || views[0]

  const sources = useMemo(() => (state.telemetry || []).map(sourceKey), [state.telemetry])
  const safeSelected = selectedSource || sources[0] || ''

  function navigate(nextView) {
    setView(nextView)
    window.history.replaceState(null, '', '/')
  }

  return (
    <div className={`shell view-${view}`}>
      <aside className="sidebar">
        <div className="brand">
          <div className="brandLogo">GT7</div>
          <div>
            <strong>Race Control</strong>
            <span>Ultra Dashboard</span>
          </div>
        </div>

        <nav className="nav">
          {views.map((item) => {
            const Icon = item.icon
            return (
              <button key={item.id} className={view === item.id ? 'navItem active' : 'navItem'} onClick={() => navigate(item.id)}>
                <Icon size={19} />
                <span>{item.label}</span>
              </button>
            )
          })}
        </nav>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <div className="eyebrow">{currentView.label}</div>
            <h1>{titleFor(view)}</h1>
          </div>

          <div className="topActions">
            <div className={`flagMini ${state.session?.flag || 'green'}`}>
              <Flag size={16} />
              {state.session?.flag || 'green'}
            </div>
            <div className="statusPill">
              <RadioTower size={18} />
              <span className={connected ? 'ok' : 'ko'}>{connected ? 'Live' : 'Offline'}</span>
            </div>
          </div>
        </header>

        {error && <div className="error">{error}</div>}

        <section className="metrics">
          <Metric icon={<Users />} label="Équipes" value={state.teams.length} />
          <Metric icon={<Activity />} label="Sources live" value={`${live}/${state.telemetry.length}`} />
          <Metric icon={<RadioTower />} label="Workers" value={workers} />
          <Metric icon={<Map />} label="Circuit" value={state.active_track?.name || 'Aucun'} />
        </section>

        {view === 'control' && <RaceControlView race={race} selectedSource={safeSelected} setSelectedSource={setSelectedSource} />}
        {view === 'teams' && <TeamsMobileView race={race} selectedSource={safeSelected} setSelectedSource={setSelectedSource} />}
        {view === 'cars' && <CarDetailView race={race} selectedSource={safeSelected} setSelectedSource={setSelectedSource} />}
        {view === 'performance' && <PerformanceView race={race} />}
        {view === 'public' && <PublicScreenView race={race} />}
        {view === 'tracks' && <TrackView race={race} />}
        {view === 'tools' && <ToolsView race={race} />}
        {view === 'events' && <EventsView race={race} />}
      </main>
    </div>
  )
}

function Metric({ icon, label, value }) {
  return <div className="metric"><div className="metricIcon">{icon}</div><div><div className="metricLabel">{label}</div><div className="metricValue">{value}</div></div></div>
}

function titleFor(view) {
  const map = {
    control: 'Vue direction de course',
    teams: 'Dashboards équipes mobile',
    cars: 'Infos voitures complètes',
    performance: 'Pneus, chronos, secteurs et delta',
    public: 'Écran public / stream',
    tracks: 'Circuit automatique',
    tools: 'Outils de course',
    events: 'Journal et exports'
  }
  return map[view] || 'GT7 Race Control'
}

function resolveInitialView() {
  const path = window.location.pathname
  if (path.startsWith('/team/')) return 'teams'
  if (path.startsWith('/car/')) return 'cars'
  if (path.startsWith('/public')) return 'public'
  return 'control'
}

function resolveInitialSource() {
  const path = window.location.pathname
  if (path.startsWith('/team/')) return decodeURIComponent(path.replace('/team/', ''))
  if (path.startsWith('/car/')) return decodeURIComponent(path.replace('/car/', ''))
  return ''
}
