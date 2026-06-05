export function fmt(value, digits = 1) {
  if (value === null || value === undefined || Number.isNaN(value)) return '—'
  if (typeof value === 'number') return value.toFixed(digits).replace(/\.0$/, '')
  return value
}

export function fmtTime(seconds) {
  const s = Math.max(0, Math.floor(seconds || 0))
  const h = Math.floor(s / 3600)
  const m = Math.floor((s % 3600) / 60)
  const sec = s % 60
  return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(sec).padStart(2, '0')}`
}

export function sourceKey(car) {
  return car?.source_id || `${car?.worker_id}:${car?.console_ip}`
}

export function teamBySource(state, sourceId) {
  return (state.teams || []).find((team) => team.source_id === sourceId)
}

export function carBySource(state, sourceId) {
  return (state.telemetry || []).find((car) => sourceKey(car) === sourceId)
}

export function activePilot(team) {
  return team?.pilots?.find((pilot) => pilot.id === team.active_pilot_id)
}

export function copyText(text) {
  return navigator.clipboard?.writeText(text)
}
