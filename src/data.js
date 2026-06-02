export const tracks = [
  { id: 'spa', country: 'Belgique', name: 'Spa-Francorchamps', length: '7.00 km', laps: 22, weather: 'Variable', model: '/assets/models/spa.gltf', layout: 'fast' },
  { id: 'yasmarina', country: 'Abu Dhabi', name: 'Yas Marina', length: '5.28 km', laps: 28, weather: 'Sec', model: '/assets/models/yasmarina.gltf', layout: 'technical' },
  { id: 'dragontrail', country: 'Original Track', name: 'Dragon Trail', length: '5.20 km', laps: 26, weather: 'Clair', model: '/assets/models/dragontrail.gltf', layout: 'coastal' },
  { id: 'bathurst', country: 'Australie', name: 'Mount Panorama', length: '6.21 km', laps: 24, weather: 'Variable', model: '/assets/models/bathurst.gltf', layout: 'mountain' },
  { id: 'nordschleife', country: 'Allemagne', name: 'Nürburgring Nordschleife', length: '20.83 km', laps: 8, weather: 'Brouillard', model: '/assets/models/nordschleife.gltf', layout: 'endurance' }
];

export const teams = [
  { id: 'scuderia', number: '01', name: 'Scuderia Corsa', origin: 'Italie', car: 'Ferrari SF90 Stradale', color: '#dc2626', points: 94 },
  { id: 'apex', number: '02', name: 'Apex Performance', origin: 'France', car: 'Porsche 911 RSR', color: '#facc15', points: 88 },
  { id: 'veloce', number: '03', name: 'Veloce Racing', origin: 'Royaume-Uni', car: 'Mixed Lineup Gr.3', color: '#3b82f6', points: 72 },
  { id: 'nightshift', number: '04', name: 'NightShift Motorsport', origin: 'Japon', car: 'Nissan GT-R GT3', color: '#a855f7', points: 63 }
];

export const drivers = [
  { number: 16, name: 'J. Villeneuve', team: 'Scuderia Corsa', car: 'Ferrari SF90', status: 'Confirmé', wins: 2, points: 52 },
  { number: 44, name: 'M. Verstappen', team: 'Apex Performance', car: 'Porsche 911 RSR', status: 'Confirmé', wins: 1, points: 49 },
  { number: 7, name: 'A. Moreau', team: 'Veloce Racing', car: 'AMG GT3', status: 'Confirmé', wins: 1, points: 43 },
  { number: 23, name: 'L. Nakamura', team: 'NightShift Motorsport', car: 'Nissan GT-R', status: 'Confirmé', wins: 0, points: 39 },
  { number: 91, name: 'S. Rossi', team: 'Scuderia Corsa', car: 'Ferrari SF90', status: 'Réserve', wins: 0, points: 33 },
  { number: 11, name: 'T. Bernard', team: 'Apex Performance', car: 'Porsche 911 RSR', status: 'Confirmé', wins: 0, points: 31 }
];

export const calendar = [
  { round: 1, track: 'Spa-Francorchamps', date: '14 juin 2026', format: 'Endurance 45 min' },
  { round: 2, track: 'Yas Marina', date: '28 juin 2026', format: 'Sprint + Endurance' },
  { round: 3, track: 'Dragon Trail', date: '12 juillet 2026', format: 'Course de nuit' },
  { round: 4, track: 'Mount Panorama', date: '26 juillet 2026', format: 'Double relais' },
  { round: 5, track: 'Nordschleife', date: '09 août 2026', format: 'Finale 60 min' }
];

export const rules = [
  { icon: 'timer', title: 'Qualifications', value: '15 minutes', text: 'Piste ouverte, tours illimités, aspiration autorisée.' },
  { icon: 'gauge', title: 'Course principale', value: '45 minutes', text: 'Carburant x3, pneus x4, stratégie libre.' },
  { icon: 'wrench', title: 'Arrêt obligatoire', value: '1 pit minimum', text: 'Changement pneus ou carburant validé par passage aux stands.' },
  { icon: 'shield-check', title: 'Fair-play', value: 'Stewards live', text: 'Pénalités post-course sur incidents signalés.' }
];
