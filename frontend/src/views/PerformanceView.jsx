import PerformancePanel from '../components/PerformancePanel'
import SectorBoard from '../components/SectorBoard'
import TyreAnalytics from '../components/TyreAnalytics'
import TrackMap from '../components/TrackMap'

export default function PerformanceView({ race }) {
  const state = { ...race.state, heatmapMode: 'all' }
  return (
    <div className="dashboardGrid">
      <section className="panel span2"><h2>Classement performance / delta</h2><PerformancePanel state={race.state} /></section>
      <section className="panel"><h2>Pneus et prédictions</h2><TyreAnalytics state={race.state} /></section>
      <section className="panel"><h2>Secteurs</h2><SectorBoard state={race.state} /></section>
      <section className="panel span2"><h2>Heatmap freinage / accélération</h2><TrackMap state={state} /></section>
    </div>
  )
}
