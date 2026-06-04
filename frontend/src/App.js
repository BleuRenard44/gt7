import React, { useState, useEffect, useRef } from 'react';
import CircuitMap from './components/CircuitMap';
import Scoreboard from './components/Scoreboard';
import TeamDashboard from './components/TeamDashboard';

function App() {
  const [playersData, setPlayersData] = useState({});
  const wsRef = useRef(null);

  useEffect(()=>{
    const ws = new WebSocket('ws://localhost:8765');
    wsRef.current = ws;
    ws.onmessage = msg => setPlayersData(JSON.parse(msg.data));
    return ()=>ws.close();
  },[]);

  return (
    <div>
      <h1>GT7 Advanced Dashboard with Teams</h1>
      <CircuitMap />
      <Scoreboard data={playersData} />
      {Object.keys(playersData).map(ip=><TeamDashboard key={ip} consoleIp={ip} ws={wsRef.current}/>)}
    </div>
  )
}

export default App;
