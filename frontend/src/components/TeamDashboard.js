import React, { useState } from 'react';

export default function TeamDashboard({ consoleIp, ws }) {
  const [teamName, setTeamName] = useState(`Team ${consoleIp}`);
  const [pilots, setPilots] = useState([]);
  const [relayOrder, setRelayOrder] = useState([]);

  const addPilot = () => {
    const name = prompt("Pilot Name:");
    const car = prompt("Car Name:");
    if (name && car) setPilots([...pilots, {name, car}]);
  }

  const updateRelay = () => {
    const order = prompt("Relay order (comma separated):");
    if(order) setRelayOrder(order.split(",").map(s=>s.trim()));
  }

  const saveTeam = () => {
    ws.send(JSON.stringify({
      action:"update_team",
      consoleIp,
      team: {teamName, pilots, relayOrder}
    }));
  }

  return (
    <div style={{border:'1px solid gray', padding:'10px', margin:'10px'}}>
      <h3>{teamName}</h3>
      <button onClick={addPilot}>Add Pilot</button>
      <button onClick={updateRelay}>Set Relay</button>
      <button onClick={saveTeam}>Save Team</button>
      <ul>{pilots.map((p,i)=><li key={i}>{p.name} ({p.car})</li>)}</ul>
      <p>Relay: {relayOrder.join(" -> ")}</p>
    </div>
  )
}
