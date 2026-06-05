import TrackMap from '../components/TrackMap'
import Scoreboard from '../components/Scoreboard'
import { fmtTime } from '../utils'

export default function PublicScreenView({ race }) {
  const { state } = race
  return (
    <div className="publicScreen">
      <section className={`publicHeader ${state.session?.flag || 'green'}`}>
        <div>
          <span>{state.session?.status || 'idle'}</span>
          <h2>{state.session?.name || 'GT7 Race'}</h2>
        </div>
        <strong>{fmtTime(state.session?.elapsed_seconds || 0)}</strong>
      </section>

      <div className="publicGrid">
        <section className="panel"><TrackMap state={state} /></section>
        <section className="panel"><Scoreboard state={state} /></section>
      </div>
    </div>
  )
}
