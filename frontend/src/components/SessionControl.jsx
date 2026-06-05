import { useState } from 'react'
import { api } from '../api'

const flags = ['green', 'yellow', 'red', 'safety_car', 'vsc', 'checkered']
const statuses = ['idle', 'practice', 'qualifying', 'race', 'finished']

export default function SessionControl({ race }) {
  const { state, refresh } = race
  const session = state.session || {}
  const [name, setName] = useState(session.name || 'GT7 Race')
  const [notes, setNotes] = useState(session.notes || '')

  async function update(payload) {
    await api.updateSession(payload)
    await refresh()
  }

  return (
    <div className="sessionControl">
      <div>
        <h2>Direction de course</h2>
        <p>Timer, type de session, drapeaux et notes officielles.</p>
      </div>

      <div className="sessionGrid">
        <label>Nom session<input value={name} onChange={(e) => setName(e.target.value)} /></label>
        <label>Notes<input value={notes} onChange={(e) => setNotes(e.target.value)} /></label>
        <button onClick={() => update({ name, notes })}>Sauvegarder</button>
      </div>

      <div className="buttonRow">
        {statuses.map((status) => (
          <button key={status} className={session.status === status ? 'activeBtn' : 'secondary'} onClick={() => update({ status })}>
            {status}
          </button>
        ))}
        <button className="secondary" onClick={() => update({ reset_timer: true })}>Reset timer</button>
      </div>

      <div className="buttonRow">
        {flags.map((flag) => (
          <button key={flag} className={session.flag === flag ? `flagBtn ${flag}` : 'secondary'} onClick={() => update({ flag })}>
            {flag}
          </button>
        ))}
      </div>

      <div className={`flagBanner ${session.flag || 'green'}`}>
        {session.flag || 'green'} · {formatTime(session.elapsed_seconds || 0)}
      </div>
    </div>
  )
}

function formatTime(seconds) {
  const s = Math.floor(seconds)
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60)
  const sec = s % 60
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`
}
