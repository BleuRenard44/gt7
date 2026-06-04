import React from 'react';

export default function Scoreboard({ data }) {
  return (
    <div>
      <h2>Scoreboard</h2>
      {Object.keys(data).map(ip => (
        <div key={ip}>
          <h3>{data[ip].team_name}</h3>
          <table border="1" cellPadding="5">
            <thead>
              <tr>
                <th>Pilot</th>
                <th>Speed</th>
                <th>RPM</th>
                <th>Gear</th>
                <th>Lap</th>
              </tr>
            </thead>
            <tbody>
              {data[ip].pilots.map(p => (
                <tr key={p.name}>
                  <td>{p.name}</td>
                  <td>{p.speed}</td>
                  <td>{p.rpm}</td>
                  <td>{p.gear}</td>
                  <td>{p.lap}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ))}
    </div>
  )
}
