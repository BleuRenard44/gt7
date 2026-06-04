import React, { useEffect, useRef, useState } from 'react';

export default function CircuitMap() {
  const canvasRef = useRef(null);
  const [playersData, setPlayersData] = useState({});

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8765');
    ws.onmessage = (msg) => setPlayersData(JSON.parse(msg.data));
    return () => ws.close();
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.strokeStyle = 'black';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(50,50);
    ctx.lineTo(750,50);
    ctx.lineTo(750,350);
    ctx.lineTo(50,350);
    ctx.closePath();
    ctx.stroke();

    let colorIndex = 0;
    const colors = ['red','blue','green','orange'];

    for (let consoleIp in playersData) {
      const consolePlayers = playersData[consoleIp]?.pilots || [];
      const color = colors[colorIndex % colors.length];
      colorIndex++;
      consolePlayers.forEach(p => {
        const x = Math.random()*700+50;
        const y = Math.random()*300+50;
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(x, y, 10, 0, 2*Math.PI);
        ctx.fill();
        ctx.fillStyle = 'black';
        ctx.fillText(`${p.name} (${p.speed} km/h)`, x + 12, y);
      });
    }
  }, [playersData]);

  return <canvas ref={canvasRef} width={800} height={400} style={{border:'1px solid black'}} />;
}
