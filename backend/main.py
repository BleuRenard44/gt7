import asyncio
import json
from gt_telem import TurismoClient
import websockets
from models import Team, Pilot

CONSOLE_IPS = ["192.168.1.101","192.168.1.102","192.168.1.103","192.168.1.104"]
all_teams = {}
clients = []

for ip in CONSOLE_IPS:
    all_teams[ip] = Team(name=f"Team {ip[-2:]}", pilots=[])

def create_client(ip):
    client = TurismoClient()
    client.connect(ps_ip=ip)
    def handle_update(telemetry):
        team = all_teams[ip]
        pilot_name = telemetry.name if hasattr(telemetry, "name") else "Player"
        pilot = next((p for p in team.pilots if p.name == pilot_name), None)
        if not pilot:
            pilot = Pilot(name=pilot_name, car=getattr(telemetry, "car", "Default"))
            team.pilots.append(pilot)
        pilot.speed = telemetry.speed
        pilot.rpm = telemetry.rpm
        pilot.gear = telemetry.gear
        pilot.current_lap = getattr(telemetry, "lap", pilot.current_lap)
        pilot.damage = getattr(telemetry, "damage", pilot.damage)
        pilot.tires = getattr(telemetry, "tires", pilot.tires)
    client.on_update = handle_update
    clients.append(client)

for ip in CONSOLE_IPS:
    create_client(ip)

async def ws_server(websocket, path):
    while True:
        try:
            data = {}
            for ip, team in all_teams.items():
                data[ip] = {
                    "team_name": team.name,
                    "pilots": [{ 
                        "name": p.name, "speed": p.speed, "rpm": p.rpm,
                        "gear": p.gear, "lap": p.current_lap,
                        "damage": p.damage, "tires": p.tires
                    } for p in team.pilots],
                    "relay_order": team.relay_order
                }
            await websocket.send(json.dumps(data))
        except:
            break
        await asyncio.sleep(0.05)

async def run_clients():
    tasks = [client.run_async() for client in clients]
    await asyncio.gather(*tasks)

async def main():
    ws = websockets.serve(ws_server, "0.0.0.0", 8765)
    await asyncio.gather(ws, run_clients())

if __name__ == "__main__":
    asyncio.run(main())
