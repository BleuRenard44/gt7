import { useMemo, useState } from 'react'
import { Circle, Flag, Play, Save, Square, Trash2 } from 'lucide-react'
import { api } from '../api'

export default function TrackRecorder({ race }) {
  const { state, refresh } = race
  const [name, setName] = useState(state.active_track?.name || 'Circuit GT7')
  const [sourceFilter, setSourceFilter] = useState('')

  const sources = useMemo(() => {
    return (state.telemetry || []).map((car) => ({
      id: car.source_id || `${car.worker_id}:${car.console_ip}`,
      label: `${car.worker_id} / ${car.console_ip}`
    }))
  }, [state.telemetry])

  async function action(fn) {
    await fn()
    await refresh()
  }

  return (
    <div className="recorder">
      <div>
        <h2>Enregistrement automatique du circuit</h2>
        <p>
          Clique sur démarrer, fais un tour propre avec une voiture, puis termine l'enregistrement.
          Le backend génère automatiquement le tracé à partir des coordonnées GT7.
        </p>
      </div>

      <div className="recorderGrid">
        <label>
          Nom du circuit
          <input value={name} onChange={(event) => setName(event.target.value)} placeholder="Trial Mountain" />
        </label>

        <label>
          Voiture de référence
          <select value={sourceFilter} onChange={(event) => setSourceFilter(event.target.value)}>
            <option value="">Toutes les sources</option>
            {sources.map((source) => <option key={source.id} value={source.id}>{source.label}</option>)}
          </select>
        </label>

        <div className="recordStatus">
          <span className={state.recording?.active ? 'recordDot on' : 'recordDot'} />
          {state.recording?.active ? `Enregistrement : ${state.recording.sample_count} points` : 'En attente'}
        </div>
      </div>

      <div className="buttonRow">
        {!state.recording?.active ? (
          <button onClick={() => action(() => api.startRecording({ name, source_filter: sourceFilter || null }))}>
            <Play size={16} /> Démarrer l'enregistrement circuit
          </button>
        ) : (
          <>
            <button onClick={() => action(() => api.finishRecording({ name, activate: true }))}>
              <Save size={16} /> Terminer & générer circuit
            </button>
            <button className="secondary" onClick={() => action(() => api.cancelRecording())}>
              <Square size={16} /> Annuler
            </button>
          </>
        )}
      </div>

      <div className="trackList">
        {(state.tracks || []).map((track) => (
          <div className="trackItem" key={track.id}>
            <div>
              <strong>{track.name}</strong>
              <span>{track.points.length} points · {track.source_count} samples</span>
            </div>
            <div className="trackActions">
              <button className={track.active ? 'activeBtn' : 'secondary'} onClick={() => action(() => api.activateTrack(track.id))}>
                <Flag size={15} /> {track.active ? 'Actif' : 'Activer'}
              </button>
              <button className="danger" onClick={() => action(() => api.deleteTrack(track.id))}>
                <Trash2 size={15} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
