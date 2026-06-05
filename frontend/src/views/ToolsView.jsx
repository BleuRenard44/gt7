import RaceTools from '../components/RaceTools'
import TeamManager from '../components/TeamManager'

export default function ToolsView({ race }) {
  return (
    <div className="dashboardGrid">
      <section className="panel span2"><h2>Race tools</h2><RaceTools race={race} /></section>
      <section className="panel span2"><h2>Équipes, pilotes et relais</h2><TeamManager race={race} /></section>
    </div>
  )
}
