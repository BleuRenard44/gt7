import SessionControl from '../components/SessionControl'
import TrackMap from '../components/TrackMap'
import Scoreboard from '../components/Scoreboard'
import MiniCarStrip from '../components/MiniCarStrip'
import EventLog from '../components/EventLog'
import PerformancePanel from '../components/PerformancePanel'
import SectorBoard from '../components/SectorBoard'
import TyreAnalytics from '../components/TyreAnalytics'

export default function RaceControlView({ race, selectedSource, setSelectedSource }) {
  const { state } = race
  return (
    <div className="dashboardGrid">
      <section className="panel span2"><SessionControl race={race} /></section>
      <section className="panel mapPanel">
        <div className="panelTitle"><h2>Carte live + heatmap</h2><span>{state.active_track?.points?.length || 0} points</span></div>
        <TrackMap state={state} selectedSource={selectedSource} setSelectedSource={setSelectedSource} />
      </section>
      <section className="panel"><h2>Classement</h2><Scoreboard state={state} selectedSource={selectedSource} setSelectedSource={setSelectedSource} /></section>
      <section className="panel span2"><h2>Performance, delta et secteurs</h2><PerformancePanel state={state} /></section>
      <section className="panel"><h2>Secteurs récents</h2><SectorBoard state={state} /></section>
      <section className="panel"><h2>Pneus</h2><TyreAnalytics state={state} /></section>
      <section className="panel span2"><h2>Voitures</h2><MiniCarStrip state={state} selectedSource={selectedSource} setSelectedSource={setSelectedSource} /></section>
      <section className="panel span2"><h2>Journal live</h2><EventLog state={state} compact /></section>
    </div>
  )
}
