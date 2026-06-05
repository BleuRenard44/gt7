import { Copy, ExternalLink, Smartphone } from 'lucide-react'
import TeamMobileDashboard from '../components/TeamMobileDashboard'
import { copyText, sourceKey, teamBySource } from '../utils'

export default function TeamsMobileView({ race, selectedSource, setSelectedSource }) {
  const { state } = race
  const sources = (state.telemetry || []).map(sourceKey)
  const selected = selectedSource || sources[0]
  const url = selected ? `${window.location.origin}/team/${encodeURIComponent(selected)}` : ''

  return (
    <div className="mobilePage">
      <section className="panel mobileSelector">
        <div>
          <h2>Dashboard téléphone équipe</h2>
          <p>Chaque équipe peut ouvrir sa propre vue sur téléphone. L'interface s'adapte automatiquement.</p>
        </div>

        <div className="inlineForm">
          <select value={selected || ''} onChange={(e) => setSelectedSource(e.target.value)}>
            <option value="">Choisir équipe</option>
            {sources.map((source) => {
              const team = teamBySource(state, source)
              return <option key={source} value={source}>{team?.name || source}</option>
            })}
          </select>
          <button onClick={() => url && copyText(url)}><Copy size={16} /> Copier lien</button>
          <a className="downloadBtn" href={url} target="_blank"><ExternalLink size={16} /> Ouvrir</a>
        </div>
        {url && <div className="shareUrl"><Smartphone size={16} /> {url}</div>}
      </section>

      <TeamMobileDashboard race={race} sourceId={selected} />
    </div>
  )
}
