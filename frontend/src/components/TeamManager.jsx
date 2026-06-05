import { useState } from 'react'
import { api } from '../api'

export default function TeamManager({ race }) {
  const { state } = race

  async function refreshAfter(action) {
    await action()
    await race.refresh()
  }

  return <div className="teamGrid">{(state.teams || []).map((team) => <TeamEditor key={team.id} team={team} refreshAfter={refreshAfter} />)}</div>
}

function TeamEditor({ team, refreshAfter }) {
  const [name, setName] = useState(team.name)
  const [color, setColor] = useState(team.color)
  const [status, setStatus] = useState(team.status || 'running')
  const [notes, setNotes] = useState(team.notes || '')
  const [pilotName, setPilotName] = useState('')
  const [pilotNumber, setPilotNumber] = useState('')
  const [pilotCar, setPilotCar] = useState('')
  const [relayPilotId, setRelayPilotId] = useState(team.pilots[0]?.id || '')

  return (
    <article className="teamCard">
      <div className="teamHeader">
        <input className="teamNameInput" value={name} onChange={(e) => setName(e.target.value)} />
        <input className="colorInput" type="color" value={color} onChange={(e) => setColor(e.target.value)} />
      </div>

      <div className="muted">Source : {team.source_id}</div>
      <div className="inlineForm">
        <select value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="running">running</option>
          <option value="pit">pit</option>
          <option value="dnf">dnf</option>
          <option value="dns">dns</option>
        </select>
        <input placeholder="Notes" value={notes} onChange={(e) => setNotes(e.target.value)} />
      </div>
      <button onClick={() => refreshAfter(() => api.upsertTeam({ name, color, source_id: team.source_id, status, notes }))}>Sauvegarder équipe</button>

      <h4>Pilotes</h4>
      <div className="inlineForm">
        <input placeholder="Nom pilote" value={pilotName} onChange={(e) => setPilotName(e.target.value)} />
        <input placeholder="N°" value={pilotNumber} onChange={(e) => setPilotNumber(e.target.value)} />
        <input placeholder="Voiture" value={pilotCar} onChange={(e) => setPilotCar(e.target.value)} />
        <button onClick={() => refreshAfter(async () => {
          if (!pilotName.trim()) return
          await api.addPilot(team.id, { name: pilotName.trim(), number: pilotNumber ? Number(pilotNumber) : null, car: pilotCar || null })
          setPilotName(''); setPilotNumber(''); setPilotCar('')
        })}>Ajouter</button>
      </div>

      <div className="pilotList">
        {team.pilots.map((pilot) => (
          <div className="pilotRow" key={pilot.id}>
            <span><strong>{pilot.name}</strong>{pilot.number ? ` #${pilot.number}` : ''}{pilot.car ? ` · ${pilot.car}` : ''}</span>
            <div>
              <button onClick={() => refreshAfter(() => api.setActivePilot(team.id, pilot.id))}>Actif</button>
              <button className="danger" onClick={() => refreshAfter(() => api.deletePilot(team.id, pilot.id))}>Suppr.</button>
            </div>
          </div>
        ))}
      </div>

      <h4>Relais</h4>
      <div className="inlineForm">
        <select value={relayPilotId} onChange={(e) => setRelayPilotId(e.target.value)}>
          <option value="">Choisir pilote</option>
          {team.pilots.map((pilot) => <option key={pilot.id} value={pilot.id}>{pilot.name}</option>)}
        </select>
        <button onClick={() => refreshAfter(() => relayPilotId ? api.addRelay(team.id, { pilot_id: relayPilotId }) : Promise.resolve())}>Ajouter relais</button>
        <button onClick={() => refreshAfter(() => api.startNextRelay(team.id))}>Relais suivant</button>
      </div>

      <ol className="relayList">
        {team.relay_order.map((relay) => {
          const pilot = team.pilots.find((p) => p.id === relay.pilot_id)
          return <li key={relay.id} className={relay.status}>{pilot?.name || 'Pilote supprimé'} · {relay.status}</li>
        })}
      </ol>
    </article>
  )
}
