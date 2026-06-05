import { useEffect, useMemo, useState } from 'react'
import { api, WS_URL } from '../api'

export function useRaceState() {
  const [state, setState] = useState({ teams: [], telemetry: [], updated_at: Date.now() / 1000 })
  const [connected, setConnected] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    let alive = true
    let ws = null
    let reconnectTimer = null

    async function initialLoad() {
      try {
        const current = await api.getState()
        if (alive) setState(current)
      } catch (err) {
        if (alive) setError(err.message)
      }
    }

    function connect() {
      ws = new WebSocket(WS_URL)

      ws.onopen = () => {
        if (!alive) return
        setConnected(true)
        setError(null)
      }

      ws.onmessage = (event) => {
        if (!alive) return
        try {
          setState(JSON.parse(event.data))
        } catch (err) {
          setError(err.message)
        }
      }

      ws.onerror = () => {
        if (!alive) return
        setError('WebSocket error')
      }

      ws.onclose = () => {
        if (!alive) return
        setConnected(false)
        reconnectTimer = setTimeout(connect, 1500)
      }
    }

    initialLoad()
    connect()

    return () => {
      alive = false
      if (reconnectTimer) clearTimeout(reconnectTimer)
      if (ws) ws.close()
    }
  }, [])

  const byTeamId = useMemo(() => {
    const map = new Map()
    for (const team of state.teams || []) map.set(team.id, team)
    return map
  }, [state.teams])

  const byConsoleIp = useMemo(() => {
    const map = new Map()
    for (const team of state.teams || []) map.set(team.console_ip, team)
    return map
  }, [state.teams])

  return { state, setState, connected, error, byTeamId, byConsoleIp }
}
