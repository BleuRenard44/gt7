import { useMemo, useState } from 'react'
import { api } from '../api'

export default function RaceTools({ race }) {
  const { state, refresh } = race
  const sources = useMemo(() => (state.teams || []).map((team) => ({ id: team.source_id, label: team.name })), [state.teams])
  const [sourceId, setSourceId] = useState('')
  const [penaltyReason, setPenaltyReason] = useState('')
  const [penaltySeconds, setPenaltySeconds] = useState(5)
  const [incidentTitle, setIncidentTitle] = useState('')
  const [incidentDescription, setIncidentDescription] = useState('')

  async function action(fn) {
    await fn()
    await refresh()
  }

  return (
    <div className="raceTools">
      <div className="toolForm">
        <label>Source
          <select value={sourceId} onChange={(e) => setSourceId(e.target.value)}>
            <option value="">Choisir source</option>
            {sources.map((s) => <option key={s.id} value={s.id}>{s.label}</option>)}
          </select>
        </label>

        <label>Pénalité
          <input placeholder="Raison" value={penaltyReason} onChange={(e) => setPenaltyReason(e.target.value)} />
        </label>

        <label>Secondes
          <input type="number" value={penaltySeconds} onChange={(e) => setPenaltySeconds(Number(e.target.value))} />
        </label>

        <button onClick={() => action(async () => {
          if (!sourceId || !penaltyReason) return
          await api.addPenalty({ source_id: sourceId, reason: penaltyReason, seconds: penaltySeconds })
          setPenaltyReason('')
        })}>Ajouter pénalité</button>

        <button className="secondary" onClick={() => action(() => sourceId ? api.startPit({ source_id: sourceId, notes: '' }) : Promise.resolve())}>
          Entrée pit
        </button>
      </div>

      <div className="toolForm">
        <label>Incident
          <input placeholder="Titre incident" value={incidentTitle} onChange={(e) => setIncidentTitle(e.target.value)} />
        </label>
        <label>Description
          <input placeholder="Description" value={incidentDescription} onChange={(e) => setIncidentDescription(e.target.value)} />
        </label>
        <button onClick={() => action(async () => {
          if (!incidentTitle) return
          await api.addIncident({ source_id: sourceId || null, title: incidentTitle, description: incidentDescription, severity: 'medium' })
          setIncidentTitle('')
          setIncidentDescription('')
        })}>Créer incident</button>
      </div>

      <div className="columns3">
        <Panel title="Pénalités">
          {(state.penalties || []).map((p) => (
            <div className="miniItem" key={p.id}>
              <span>{p.source_id} · +{p.seconds}s · {p.reason}</span>
              <button className={p.served ? 'activeBtn' : 'secondary'} onClick={() => action(() => api.updatePenalty(p.id, { served: !p.served }))}>
                {p.served ? 'Servie' : 'À servir'}
              </button>
            </div>
          ))}
        </Panel>

        <Panel title="Incidents">
          {(state.incidents || []).map((i) => (
            <div className="miniItem" key={i.id}>
              <span>{i.title} · {i.source_id || 'global'}</span>
              <button className={i.resolved ? 'activeBtn' : 'secondary'} onClick={() => action(() => api.updateIncident(i.id, { resolved: !i.resolved }))}>
                {i.resolved ? 'Résolu' : 'Ouvert'}
              </button>
            </div>
          ))}
        </Panel>

        <Panel title="Pit stops">
          {(state.pit_stops || []).map((p) => (
            <div className="miniItem" key={p.id}>
              <span>{p.source_id} · {p.ended_at ? 'terminé' : 'en cours'}</span>
              {!p.ended_at && <button onClick={() => action(() => api.finishPit(p.id, { notes: p.notes || '' }))}>Sortie</button>}
            </div>
          ))}
        </Panel>
      </div>
    </div>
  )
}

function Panel({ title, children }) {
  return <div className="miniPanel"><h3>{title}</h3>{children}</div>
}
