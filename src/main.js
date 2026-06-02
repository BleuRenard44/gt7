import './styles.css';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { createIcons, icons } from 'lucide';
import { tracks, teams, drivers, calendar, rules } from './data.js';

const app = document.querySelector('#app');

app.innerHTML = `
  <div class="noise">
    <header class="site-header">
      <nav class="container nav" aria-label="Navigation principale">
        <a class="brand" href="#home" aria-label="GT7 League Hub"><span class="brand-mark">GT</span><span>GT7 // League</span></a>
        <button class="menu-toggle" type="button" aria-label="Ouvrir le menu" aria-expanded="false"><i data-lucide="menu"></i></button>
        <div class="nav-links" id="nav-links">
          <a href="#tracks">Circuits</a><a href="#format">Format</a><a href="#teams">Équipes</a><a href="#drivers">Pilotes</a><a href="#calendar">Calendrier</a><a href="#standings">Classement</a>
        </div>
      </nav>
    </header>
    <main>
      <section class="hero" id="home">
        <div class="hero-grid"></div>
        <div class="hero-content">
          <div class="kicker">// Premium championship control room</div>
          <h1>Versus<br/>Mode</h1>
          <p class="hero-copy">Un vrai hub GT7 complet pour présenter ton championnat : scanner véhicules, circuits 3D, règlement, roster, calendrier et classement dynamique côté front.</p>
          <div class="hero-actions"><a class="btn primary" href="#standings"><i data-lucide="trophy"></i> Voir le classement</a><a class="btn ghost" href="#tracks"><i data-lucide="radar"></i> Scanner les circuits</a></div>
          <div class="scan-card">
            <div class="car-stage" id="car-stage" aria-label="Comparateur Ferrari Porsche interactif">
              <div class="car ferrari">SF90</div><div class="car porsche" id="reveal-mask">911 RSR</div>
            </div>
            <p class="scan-hint">Passe la souris ou le doigt sur la zone pour révéler la voiture adverse</p>
          </div>
        </div>
      </section>
      <section class="section dark" id="tracks"><div class="container"><div class="section-head"><div><div class="kicker">Telemetry data</div><h2>3D Track Scanner</h2></div><p class="section-lead">Les fichiers GLTF sont chargés automatiquement depuis <strong>public/assets/models</strong>. Quand un modèle est absent, un tracé procédural prend le relais.</p></div><div class="track-layout"><div class="track-list" id="track-list"></div><div class="viewer"><div id="canvas-container"></div><div class="loader" id="track-loader">Chargement du maillage</div><div class="viewer-overlay"><span class="pill" id="track-name">Spa-Francorchamps</span><span class="pill">Orbit: drag • Zoom: wheel</span></div></div></div></div></section>
      <section class="section" id="format"><div class="container"><div class="section-head"><div><div class="kicker">// Race manual</div><h2>Format de compétition</h2></div><p class="section-lead">Un règlement clair, lisible et prêt pour une ligue privée ou publique.</p></div><div class="cards">${rules.map(rule => `<article class="card"><div class="icon-box"><i data-lucide="${rule.icon}"></i></div><h3>${rule.title}</h3><div class="value">${rule.value}</div><p>${rule.text}</p></article>`).join('')}</div></div></section>
      <section class="section dark" id="teams"><div class="container"><div class="section-head"><div><div class="kicker">// Constructeurs</div><h2>Écuries officielles</h2></div></div><div class="team-grid">${teams.map(team => `<article class="card team-card" style="--team-color:${team.color}"><div class="kicker">Team // ${team.number}</div><h3>${team.name}</h3><div class="value">${team.points} pts</div><p>${team.car}<br>${team.origin}</p></article>`).join('')}</div></div></section>
      <section class="section" id="drivers"><div class="container"><div class="section-head"><div><div class="kicker">// Roster</div><h2>Pilotes engagés</h2></div></div><div class="table-wrap"><table><thead><tr><th>#</th><th>Pilote</th><th>Écurie</th><th>Voiture</th><th>Victoires</th><th>Statut</th><th class="points">Pts</th></tr></thead><tbody>${drivers.map(d => `<tr><td>#${d.number}</td><td>${d.name}</td><td class="muted">${d.team}</td><td>${d.car}</td><td>${d.wins}</td><td><span class="status">${d.status}</span></td><td class="points">${d.points}</td></tr>`).join('')}</tbody></table></div></div></section>
      <section class="section dark" id="calendar"><div class="container"><div class="section-head"><div><div class="kicker">// Season 2026</div><h2>Calendrier</h2></div></div><div class="calendar">${calendar.map(r => `<article class="calendar-row"><div class="round">ROUND ${r.round}</div><strong>${r.track}</strong><span class="muted">${r.date}</span><span>${r.format}</span></article>`).join('')}</div></div></section>
      <section class="section" id="standings"><div class="container"><div class="section-head"><div><div class="kicker">// Scoreboard</div><h2>Classement championnat</h2></div><p class="section-lead">Classement généré depuis les données JS, facile à brancher plus tard sur une API, Supabase ou Google Sheets.</p></div><div class="table-wrap"><table><thead><tr><th>Position</th><th>Pilote</th><th>Écurie</th><th>Victoires</th><th class="points">Points</th></tr></thead><tbody>${[...drivers].sort((a,b)=>b.points-a.points).map((d,i) => `<tr><td>${i+1}</td><td>${d.name}</td><td class="muted">${d.team}</td><td>${d.wins}</td><td class="points">${d.points}</td></tr>`).join('')}</tbody></table></div></div></section>
    </main>
    <footer class="footer"><div class="container">© 2026 GT7 League Hub • Premium scan system • Ready to deploy</div></footer>
  </div>`;

createIcons({ icons });

const navLinks = document.querySelector('#nav-links');
const menuToggle = document.querySelector('.menu-toggle');
menuToggle?.addEventListener('click', () => {
  const open = navLinks.classList.toggle('open');
  menuToggle.setAttribute('aria-expanded', String(open));
});
navLinks?.addEventListener('click', () => navLinks.classList.remove('open'));

const carStage = document.querySelector('#car-stage');
const revealMask = document.querySelector('#reveal-mask');
function revealAt(clientX, clientY, radius = 132) {
  const rect = revealMask.getBoundingClientRect();
  revealMask.style.clipPath = `circle(${radius}px at ${clientX - rect.left}px ${clientY - rect.top}px)`;
}
carStage?.addEventListener('mousemove', e => revealAt(e.clientX, e.clientY));
carStage?.addEventListener('touchmove', e => { const t = e.touches[0]; if (t) revealAt(t.clientX, t.clientY, 110); }, { passive: true });
carStage?.addEventListener('mouseleave', () => { revealMask.style.clipPath = 'circle(0 at 0 0)'; });

const trackList = document.querySelector('#track-list');
trackList.innerHTML = tracks.map((track, index) => `<button class="track-btn ${index === 0 ? 'active' : ''}" type="button" data-track-id="${track.id}"><span><small>${track.country}</small><strong>${track.name}</strong></span><span class="track-meta">${track.length}<br>${track.laps} tours</span></button>`).join('');

let scene, camera, renderer, controls, currentModel, animationId;
const container = document.querySelector('#canvas-container');
const loader = document.querySelector('#track-loader');
const trackName = document.querySelector('#track-name');

function initThree() {
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x030303);
  camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 1000);
  camera.position.set(0, 42, 74);
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(container.clientWidth, container.clientHeight);
  container.appendChild(renderer.domElement);
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.055;
  controls.minDistance = 24;
  controls.maxDistance = 150;
  scene.add(new THREE.AmbientLight(0xffffff, 0.75));
  const red = new THREE.DirectionalLight(0xdc2626, 2.2); red.position.set(22, 64, 28); scene.add(red);
  const white = new THREE.DirectionalLight(0xffffff, 1.1); white.position.set(-40, 42, -20); scene.add(white);
  const grid = new THREE.GridHelper(110, 34, 0x333333, 0x111111); grid.position.y = -12; scene.add(grid);
  loadTrack(tracks[0]);
  animate();
}

function proceduralGeometry(layout) {
  switch (layout) {
    case 'technical': return new THREE.IcosahedronGeometry(16, 2);
    case 'coastal': return new THREE.TorusGeometry(17, 3, 18, 72);
    case 'mountain': return new THREE.CylinderGeometry(11, 18, 24, 5, 5, true);
    case 'endurance': return new THREE.TorusKnotGeometry(17, 1.7, 180, 10, 4, 7);
    default: return new THREE.TorusKnotGeometry(14, 2.6, 160, 14, 2, 3);
  }
}
function addFallback(track) {
  const material = new THREE.MeshStandardMaterial({ color: 0xdc2626, emissive: 0x240000, wireframe: true, roughness: .62 });
  currentModel = new THREE.Mesh(proceduralGeometry(track.layout), material);
  if (track.layout !== 'mountain') currentModel.rotation.x = Math.PI / 2;
  scene.add(currentModel);
}
function loadTrack(track) {
  loader.classList.add('visible');
  trackName.textContent = track.name;
  if (currentModel) scene.remove(currentModel);
  const gltfLoader = new GLTFLoader();
  gltfLoader.load(track.model, gltf => {
    currentModel = gltf.scene;
    currentModel.traverse(node => {
      if (node.isMesh) {
        node.material = new THREE.MeshStandardMaterial({ color: 0xdc2626, emissive: 0x1a0000, wireframe: true });
      }
    });
    scene.add(currentModel);
    loader.classList.remove('visible');
  }, undefined, () => {
    addFallback(track);
    loader.classList.remove('visible');
  });
}
function animate() {
  animationId = requestAnimationFrame(animate);
  if (currentModel) currentModel.rotation.z += 0.0022;
  controls?.update();
  renderer?.render(scene, camera);
}
trackList.addEventListener('click', e => {
  const button = e.target.closest('.track-btn');
  if (!button) return;
  document.querySelectorAll('.track-btn').forEach(btn => btn.classList.remove('active'));
  button.classList.add('active');
  const track = tracks.find(item => item.id === button.dataset.trackId);
  if (track) loadTrack(track);
});
window.addEventListener('resize', () => {
  if (!container || !camera || !renderer) return;
  camera.aspect = container.clientWidth / container.clientHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(container.clientWidth, container.clientHeight);
});
initThree();
