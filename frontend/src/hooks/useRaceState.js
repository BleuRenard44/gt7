import { useEffect, useState } from 'react'
import { api, WS_URL } from '../api'

export function useRaceState() {
  const [state, setState] = useState({
    teams: [],
    telemetry: [],
    tracks: [],
    active_track: null,
    recording: { active: false, sample_count: 0 },
    updated_at: Date.now() / 1000
  })
  const [connected, setConnected] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    let alive = true
    let socket = null
    let timer = null

    api.getState().then((data) => alive && setState(data)).catch((err) => alive && setError(err.message))

    function connect() {
      socket = new WebSocket(WS_URL)
      socket.onopen = () => { if (alive) { setConnected(true); setError(null) } }
      socket.onmessage = (event) => { if (alive) setState(JSON.parse(event.data)) }
      socket.onerror = () => { if (alive) setError('Erreur WebSocket') }
      socket.onclose = () => {
        if (!alive) return
        setConnected(false)
        timer = setTimeout(connect, 1500)
      }
    }

    connect()

    return () => {
      alive = false
      if (timer) clearTimeout(timer)
      if (socket) socket.close()
    }
  }, [])

  async function refresh() {
    const fresh = await api.getState()
    setState(fresh)
  }

  return { state, setState, connected, error, refresh }
}
