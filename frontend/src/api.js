export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || window.localStorage.getItem('GT7_API_BASE_URL') || `${window.location.protocol}//${window.location.hostname}:8000`
export const WS_URL = import.meta.env.VITE_WS_URL || window.localStorage.getItem('GT7_WS_URL') || `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.hostname}:8000/ws`

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options
  })
  if (!response.ok) {
    const text = await response.text()
    throw new Error(text)
  }
  return response.status === 204 ? null : response.json()
}

export const api = {
  getState: () => request('/api/state'),
  updateSession: (payload) => request('/api/session', { method: 'POST', body: JSON.stringify(payload) }),

  upsertTeam: (payload) => request('/api/teams', { method: 'POST', body: JSON.stringify(payload) }),
  addPilot: (teamId, payload) => request(`/api/teams/${teamId}/pilots`, { method: 'POST', body: JSON.stringify(payload) }),
  deletePilot: (teamId, pilotId) => request(`/api/teams/${teamId}/pilots/${pilotId}`, { method: 'DELETE' }),
  addRelay: (teamId, payload) => request(`/api/teams/${teamId}/relays`, { method: 'POST', body: JSON.stringify(payload) }),
  startNextRelay: (teamId) => request(`/api/teams/${teamId}/relays/start-next`, { method: 'POST' }),
  setActivePilot: (teamId, pilotId) => request(`/api/teams/${teamId}/active-pilot`, { method: 'POST', body: JSON.stringify({ pilot_id: pilotId }) }),

  startRecording: (payload) => request('/api/tracks/recording/start', { method: 'POST', body: JSON.stringify(payload) }),
  cancelRecording: () => request('/api/tracks/recording/cancel', { method: 'POST' }),
  finishRecording: (payload) => request('/api/tracks/recording/finish', { method: 'POST', body: JSON.stringify(payload) }),
  activateTrack: (trackId) => request('/api/tracks/activate', { method: 'POST', body: JSON.stringify({ track_id: trackId }) }),
  deleteTrack: (trackId) => request(`/api/tracks/${trackId}`, { method: 'DELETE' }),

  addPenalty: (payload) => request('/api/penalties', { method: 'POST', body: JSON.stringify(payload) }),
  updatePenalty: (penaltyId, payload) => request(`/api/penalties/${penaltyId}`, { method: 'POST', body: JSON.stringify(payload) }),

  addIncident: (payload) => request('/api/incidents', { method: 'POST', body: JSON.stringify(payload) }),
  updateIncident: (incidentId, payload) => request(`/api/incidents/${incidentId}`, { method: 'POST', body: JSON.stringify(payload) }),

  startPit: (payload) => request('/api/pit-stops', { method: 'POST', body: JSON.stringify(payload) }),
  finishPit: (pitId, payload) => request(`/api/pit-stops/${pitId}/finish`, { method: 'POST', body: JSON.stringify(payload) })
}
