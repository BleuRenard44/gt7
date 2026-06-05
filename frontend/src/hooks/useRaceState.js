import { useEffect, useMemo, useState } from 'react'
import { api, WS_URL } from '../api'

export function useRaceState() {
  const [state, setState] = useState({ teams: [], telemetry: [], updated_at: Date.now() / 1000 })
  const [connected, setConnected] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    let alive = true
    let socket = null
    let reconnectTimer = null

    api.getState().then((data) => alive && setState(data)).catch((err) => alive && setError(err.message))

    function connect() {
      socket = new WebSocket(WS_URL)

      socket.onopen = () => {
        if (!alive) return
        setConnected(true)
        setError(null)
      }

      socket.onmessage = (event) => {
        if (!alive) return
        try {
          setState(JSON.parse(event.data))
        } catch (err) {
          setError(err.message)
        }
      }

      socket.onclose = () => {
        if (!alive) return
        setConnected(false)
        reconnectTimer = setTimeout(connect, 1500)
      }

      socket.onerror = () => {
        if (!alive) return
        setError('Erreur WebSocket')
      }
    }

    connect()

    return () => {
      alive = false
      if (reconnectTimer) clearTimeout(reconnectTimer)
      if (socket) socket.close()
    }
  }, [])

  const teamsById = useMemo(() => new Map((state.teams || []).map((team) => [team.id, team])), [state.teams])

  return { state, setState, connected, error, teamsById }
}
