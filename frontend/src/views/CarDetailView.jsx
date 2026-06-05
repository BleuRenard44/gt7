import CompleteCarInfo from '../components/CompleteCarInfo'
import SourcePicker from '../components/SourcePicker'

export default function CarDetailView({ race, selectedSource, setSelectedSource }) {
  return (
    <div className="dashboardGrid">
      <section className="panel span2">
        <h2>Sélection voiture</h2>
        <SourcePicker state={race.state} selectedSource={selectedSource} setSelectedSource={setSelectedSource} />
      </section>
      <section className="panel span2">
        <CompleteCarInfo state={race.state} sourceId={selectedSource} />
      </section>
    </div>
  )
}
