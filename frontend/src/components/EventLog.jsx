export default function EventLog({ state }) {
  const events = [...(state.event_log || [])].reverse().slice(0, 80)
  return (
    <div className="eventLog">
      {events.map((event) => (
        <div className="eventItem" key={event.id}>
          <span className="eventType">{event.type}</span>
          <span>{new Date(event.created_at * 1000).toLocaleTimeString()}</span>
          <strong>{event.source_id || 'global'}</strong>
          <p>{event.message}</p>
        </div>
      ))}
    </div>
  )
}
