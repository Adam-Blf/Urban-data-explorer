const API = (typeof window !== "undefined" && window.URBAN_API) || "http://localhost:8000";

const state = { data: null, indicator: "prix_m2_median", year: null };

async function boot() {
  const [geo, indicators] = await Promise.all([
    fetch(`${API}/arrondissements`).then(r => r.json()),
    fetch(`${API}/indicators`).then(r => r.json()),
  ]);
  state.data = geo;

  const sel = document.getElementById("indicator");
  for (const [k, label] of Object.entries(indicators)) {
    const o = document.createElement("option");
    o.value = k; o.textContent = label; sel.appendChild(o);
  }
  sel.value = state.indicator;
  sel.onchange = () => { state.indicator = sel.value; paint(); };

  // Populate compare dropdowns
  const cmpA = document.getElementById("cmpA");
  const cmpB = document.getElementById("cmpB");
  for (const f of geo.features) {
    const label = `${f.properties.code_ar}e · ${f.properties.l_ar || ""}`;
    [cmpA, cmpB].forEach(s => {
      const o = document.createElement("option");
      o.value = f.properties.code_ar; o.textContent = label;
      s.appendChild(o);
    });
  }
  cmpA.onchange = cmpB.onchange = compare;

  initMap(geo);
}

function initMap(geo) {
  const map = new maplibregl.Map({
    container: "map",
    style: "https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json",
    center: [2.3522, 48.8566],
    zoom: 11.2,
  });
  map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "top-right");

  map.on("load", () => {
    map.addSource("arr", { type: "geojson", data: geo });
    map.addLayer({
      id: "arr-fill",
      type: "fill",
      source: "arr",
      paint: {
        "fill-color": choroplethExpr(state.indicator, geo),
        "fill-opacity": 0.78,
        "fill-outline-color": "#0f1115",
      },
    });
    map.addLayer({
      id: "arr-line",
      type: "line",
      source: "arr",
      paint: { "line-color": "#0f1115", "line-width": 1 },
    });
    map.on("click", "arr-fill", e => showDetail(e.features[0].properties));
    map.on("mouseenter", "arr-fill", () => (map.getCanvas().style.cursor = "pointer"));
    map.on("mouseleave", "arr-fill", () => (map.getCanvas().style.cursor = ""));
    window._map = map;
  });
}

function values(geo, key) {
  return geo.features.map(f => +f.properties[key]).filter(v => !Number.isNaN(v));
}

function quantile(arr, q) {
  const s = [...arr].sort((a, b) => a - b);
  return s[Math.floor((s.length - 1) * q)];
}

function choroplethExpr(key, geo) {
  const vals = values(geo, key);
  if (!vals.length) return "#444";
  const stops = [0.0, 0.2, 0.4, 0.6, 0.8, 1.0].map(q => quantile(vals, q));
  const colors = ["#1b2a4e", "#274472", "#3c6997", "#5885af", "#a7c5eb", "#f0a202"];
  const expr = ["interpolate", ["linear"], ["to-number", ["get", key]]];
  stops.forEach((v, i) => { expr.push(v, colors[i]); });
  return expr;
}

function paint() {
  if (!window._map || !state.data) return;
  window._map.setPaintProperty("arr-fill", "fill-color", choroplethExpr(state.indicator, state.data));
}

function showDetail(props) {
  const el = document.getElementById("detail");
  const rows = [
    ["Arrondissement", `${props.code_ar}e · ${props.l_ar || ""}`],
    ["Prix m² médian", fmt(props.prix_m2_median, "€")],
    ["Dynamique 5 ans", fmt(props.dynamique_immo_pct, "%")],
    ["Tension locative", fmt(props.tension_locative)],
    ["Mixité sociale", fmt(props.mixite_sociale)],
  ];
  el.innerHTML = `<h3>${props.l_ar || "Arrondissement " + props.code_ar}</h3>` +
    rows.map(([k, v]) => `<div class="kv"><span>${k}</span><strong>${v}</strong></div>`).join("") +
    `<canvas id="ts-chart" height="160" style="margin-top:12px"></canvas>`;
  loadTimeseries(props.code_ar);
}

async function loadTimeseries(code) {
  try {
    const r = await fetch(`${API}/timeseries/${code}?indicator=prix_m2_median`).then(r => r.json());
    const ctx = document.getElementById("ts-chart").getContext("2d");
    new Chart(ctx, {
      type: "line",
      data: {
        labels: r.points.map(p => p.annee),
        datasets: [{ label: "Prix m² médian", data: r.points.map(p => p.value), borderColor: "#6aa9ff", tension: 0.25 }],
      },
      options: { plugins: { legend: { display: false } }, scales: { y: { ticks: { color: "#8a93a2" } }, x: { ticks: { color: "#8a93a2" } } } },
    });
  } catch (e) { console.warn("timeseries error", e); }
}

async function compare() {
  const a = document.getElementById("cmpA").value;
  const b = document.getElementById("cmpB").value;
  if (!a || !b || a === b) return;
  const r = await fetch(`${API}/compare?a=${a}&b=${b}`).then(r => r.json());
  const el = document.getElementById("cmp-result");
  el.innerHTML = `
    <div class="kv"><span>Prix m² A</span><strong>${fmt(r.a.prix_m2_median, "€")}</strong></div>
    <div class="kv"><span>Prix m² B</span><strong>${fmt(r.b.prix_m2_median, "€")}</strong></div>
    <div class="kv"><span>Écart</span><strong>${fmt((r.a.prix_m2_median - r.b.prix_m2_median), "€")}</strong></div>`;
}

function fmt(v, unit = "") {
  if (v === null || v === undefined || Number.isNaN(+v)) return "—";
  return Math.round(+v).toLocaleString("fr-FR") + (unit ? " " + unit : "");
}

boot().catch(err => {
  document.getElementById("detail").innerHTML =
    `<p class="hint">API non joignable (${API}).<br>Lance <code>uvicorn api.main:app</code> puis <code>python -m pipeline.run</code>.</p>`;
  console.error(err);
});
