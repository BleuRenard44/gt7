export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
export const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {})
    },
    ...options
  })

  if (!response.ok) {
    const text = await response.text()
    throw new Error(text || `HTTP ${response.status}`)
  }

  if (response.status === 204) return null
  return response.json()
}

export const api = {
  getState: () => request('/api/state'),

  upsertTeam: (payload) =>
    request('/api/teams', {
      method: 'POST',
      body: JSON.stringify(payload)
    }),

  addPilot: (teamId, payload) =>
    request(`/api/teams/${teamId}/pilots`, {
      method: 'POST',
      body: JSON.stringify(payload)
    }),

  deletePilot: (teamId, pilotId) =>
    request(`/api/teams/${teamId}/pilots/${pilotId}`, {
      method: 'DELETE'
    }),

  addRelay: (teamId, payload) =>
    request(`/api/teams/${teamId}/relays`, {
      method: 'POST',
      body: JSON.stringify(payload)
    }),

  startNextRelay: (teamId) =>
    request(`/api/teams/${teamId}/relays/start-next`, {
      method: 'POST'
    }),

  setActivePilot: (teamId, pilotId) =>
    request(`/api/teams/${teamId}/active-pilot`, {
      method: 'POST',
      body: JSON.stringify({ pilot_id: pilotId })
    })
}
