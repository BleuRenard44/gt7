import TrackRecorder from '../components/TrackRecorder'
import TrackMap from '../components/TrackMap'

export default function TrackView({ race }) {
  return (
    <div className="dashboardGrid">
      <section className="panel span2"><TrackRecorder race={race} /></section>
      <section className="panel span2"><TrackMap state={race.state} /></section>
    </div>
  )
}
