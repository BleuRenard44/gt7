import EventLog from '../components/EventLog'
import Exports from '../components/Exports'

export default function EventsView({ race }) {
  return (
    <div className="dashboardGrid">
      <section className="panel span2"><h2>Exports</h2><Exports /></section>
      <section className="panel span2"><h2>Journal complet</h2><EventLog state={race.state} /></section>
    </div>
  )
}
