export default function GaugeBar({ label, value, max = 100, suffix = '', reverse = false }) {
  const ratio = Math.max(0, Math.min(1, (Number(value) || 0) / max))
  return (
    <div className="gaugeBar">
      <div className="gaugeTop"><span>{label}</span><strong>{value == null ? '—' : `${Math.round(value)}${suffix}`}</strong></div>
      <div className="gaugeTrack"><div className={reverse ? 'gaugeFill reverse' : 'gaugeFill'} style={{ width: `${ratio * 100}%` }} /></div>
    </div>
  )
}
