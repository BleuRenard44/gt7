import { API_BASE_URL } from '../api'

export default function Exports() {
  return (
    <div className="buttonRow">
      <a className="downloadBtn" href={`${API_BASE_URL}/api/export/state.json`} target="_blank">Export JSON</a>
      <a className="downloadBtn" href={`${API_BASE_URL}/api/export/scoreboard.csv`} target="_blank">Scoreboard CSV</a>
      <a className="downloadBtn" href={`${API_BASE_URL}/api/export/events.csv`} target="_blank">Journal CSV</a>
      <a className="downloadBtn" href={`${API_BASE_URL}/api/export/performance.csv`} target="_blank">Performance CSV</a>
    </div>
  )
}
