import { useState } from 'react'
import { api } from '../api'

export default function TeamManager({ race }) {
  const { state } = race

  async function refreshAfter(action) {
    await action()
    const fresh = await api.getState()
    race.setState(fresh)
  }

  return (
    <div className="teamGrid">
      {(state.teams || []).map((team) => (
        <TeamEditor key={team.id} team={team} refreshAfter={refreshAfter} />
      ))}
    </div>
  )
}

function TeamEditor({ team, refreshAfter }) {
  const [name, setName] = useState(team.name)
  const [color, setColor] = useState(team.color)
  const [pilotName, setPilotName] = useState('')
  const [pilotNumber, setPilotNumber] = useState('')
  const [pilotCar, setPilotCar] = useState('')
  const [relayPilotId, setRelayPilotId] = useState(team.pilots[0]?.id || '')

  return (
    <article className="teamCard">
      <div className="teamHeader">
        <input className="teamNameInput" value={name} onChange={(event) => setName(event.target.value)} />
        <input className="colorInput" type="color" value={color} onChange={(event) => setColor(event.target.value)} />
      </div>

      <div className="muted">Console : {team.console_ip}</div>

      <button
        onClick={() =>
          refreshAfter(() =>
            api.upsertTeam({
              name,
              color,
              console_ip: team.console_ip
            })
          )
        }
      >
        Sauvegarder équipe
      </button>

      <h4>Pilotes</h4>
      <div className="inlineForm">
        <input placeholder="Nom pilote" value={pilotName} onChange={(event) => setPilotName(event.target.value)} />
        <input placeholder="N°" value={pilotNumber} onChange={(event) => setPilotNumber(event.target.value)} />
        <input placeholder="Voiture" value={pilotCar} onChange={(event) => setPilotCar(event.target.value)} />
        <button
          onClick={() =>
            refreshAfter(async () => {
              if (!pilotName.trim()) return
              await api.addPilot(team.id, {
                name: pilotName.trim(),
                number: pilotNumber ? Number(pilotNumber) : null,
                car: pilotCar || null
              })
              setPilotName('')
              setPilotNumber('')
              setPilotCar('')
            })
          }
        >
          Ajouter
        </button>
      </div>

      <div className="pilotList">
        {team.pilots.map((pilot) => (
          <div className="pilotRow" key={pilot.id}>
            <span>
              <strong>{pilot.name}</strong>
              {pilot.number ? ` #${pilot.number}` : ''}
              {pilot.car ? ` · ${pilot.car}` : ''}
            </span>
            <div>
              <button onClick={() => refreshAfter(() => api.setActivePilot(team.id, pilot.id))}>
                Actif
              </button>
              <button className="danger" onClick={() => refreshAfter(() => api.deletePilot(team.id, pilot.id))}>
                Suppr.
              </button>
            </div>
          </div>
        ))}
      </div>

      <h4>Relais</h4>
      <div className="inlineForm">
        <select value={relayPilotId} onChange={(event) => setRelayPilotId(event.target.value)}>
          <option value="">Choisir pilote</option>
          {team.pilots.map((pilot) => (
            <option key={pilot.id} value={pilot.id}>
              {pilot.name}
            </option>
          ))}
        </select>
        <button
          onClick={() =>
            refreshAfter(() =>
              relayPilotId
                ? api.addRelay(team.id, {
                    pilot_id: relayPilotId,
                    expected_lap_start: null,
                    expected_lap_end: null
                  })
                : Promise.resolve()
            )
          }
        >
          Ajouter relais
        </button>
        <button onClick={() => refreshAfter(() => api.startNextRelay(team.id))}>Relais suivant</button>
      </div>

      <ol className="relayList">
        {team.relay_order.map((stint) => {
          const pilot = team.pilots.find((item) => item.id === stint.pilot_id)
          return (
            <li key={stint.id} className={stint.status}>
              {pilot?.name || 'Pilote supprimé'} · {stint.status}
            </li>
          )
        })}
      </ol>
    </article>
  )
}
