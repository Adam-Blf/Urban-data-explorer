const apiBase = "http://localhost:8000";

const state = {
  token: localStorage.getItem("ude-token") || "",
  sources: [],
  dashboard: [],
  timeline: [],
  events: [],
  pipeline: null,
};

const el = (id) => document.getElementById(id);

function headers() {
  // Send the API token only when the user chose to store one locally.
  const value = state.token.trim();
  return value ? { "X-API-Key": value } : {};
}

async function apiFetch(path) {
  const res = await fetch(`${apiBase}${path}`, { headers: headers() });
  if (!res.ok) {
    throw new Error(await res.text());
  }
  return res.json();
}

function setText(id, text) {
  el(id).textContent = text;
}

function renderStack(container, items, renderItem) {
  container.innerHTML = "";
  items.forEach((item) => {
    const row = document.createElement("div");
    row.className = "row";
    row.innerHTML = renderItem(item);
    container.appendChild(row);
  });
}

function scoreClass(value) {
  if (value >= 75) return "score-high";
  if (value >= 45) return "score-mid";
  return "score-low";
}

function renderDashboard() {
  // Rebuild the source list, the KPI cards, and the family filter together.
  const query = el("source-search").value.toLowerCase().trim();
  const family = el("family-filter").value;
  const filteredSources = state.sources.filter((source) => {
    const matchesQuery =
      !query ||
      source.title.toLowerCase().includes(query) ||
      source.family.toLowerCase().includes(query) ||
      source.provider.toLowerCase().includes(query);
    const matchesFamily = family === "all" || source.family === family;
    return matchesQuery && matchesFamily;
  });

  renderStack(
    el("sources-output"),
    filteredSources,
    (source) => `
      <strong>${source.title}</strong>
      <span>${source.family} · ${source.provider}${source.metadata_only ? " · métadonnées" : ""}</span>
      <a href="${source.catalog_url}" target="_blank" rel="noreferrer">Source</a>
    `
  );

  const sourceFamilies = [...new Set(state.sources.map((source) => source.family))].sort();
  const familySelect = el("family-filter");
  const current = familySelect.value || "all";
  familySelect.innerHTML = '<option value="all">Toutes les familles</option>';
  sourceFamilies.forEach((familyName) => {
    const option = document.createElement("option");
    option.value = familyName;
    option.textContent = familyName;
    familySelect.appendChild(option);
  });
  familySelect.value = sourceFamilies.includes(current) ? current : "all";

  el("metric-sources").textContent = String(state.sources.length);
  el("metric-families").textContent = String(sourceFamilies.length);
  el("metric-arrondissements").textContent = String(state.dashboard.length);

  const districtGrid = el("dashboard-grid");
  districtGrid.innerHTML = "";
  state.dashboard.forEach((row) => {
    const card = document.createElement("article");
    card.className = `district-card ${scoreClass(row.attractiveness_index)}`;
    card.innerHTML = `
      <div class="district-head">
        <strong>${row.arrondissement_code}</strong>
        <span>${row.attractiveness_index.toFixed(0)}</span>
      </div>
      <div class="district-bars">
        <div><span>Accessibilité</span><div class="bar"><i style="width:${row.accessibility_index}%"></i></div></div>
        <div><span>Attractivité</span><div class="bar"><i style="width:${row.attractiveness_index}%"></i></div></div>
        <div><span>Pression</span><div class="bar"><i style="width:${row.pressure_index}%"></i></div></div>
      </div>
      <small>${row.green_space_count} espaces verts · ${row.mobility_count} mobilités · ${row.public_service_count} services</small>
    `;
    districtGrid.appendChild(card);
  });
}

function renderTimeline() {
  // Draw a lightweight SVG bar chart to avoid extra frontend dependencies.
  const container = el("timeline-chart");
  const values = state.timeline.slice(0, 12).map((row) => ({
    label: `${row.arrondissement_code} ${String(row.year).slice(-2)}/${String(row.month).padStart(2, "0")}`,
    value: row.record_count,
  }));
  const width = 900;
  const height = 280;
  const max = Math.max(...values.map((item) => item.value), 1);
  const barWidth = values.length ? width / values.length - 10 : 0;
  container.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Charge par mois">
      ${values
        .map((item, index) => {
          const barHeight = Math.max((item.value / max) * 180, 10);
          const x = index * (barWidth + 10) + 20;
          const y = 230 - barHeight;
          return `
            <g transform="translate(${x},0)">
              <rect x="0" y="${y}" width="${barWidth}" height="${barHeight}" rx="10"></rect>
              <text x="${barWidth / 2}" y="252" text-anchor="middle">${item.label}</text>
              <text x="${barWidth / 2}" y="${Math.max(y - 6, 16)}" text-anchor="middle">${item.value}</text>
            </g>
          `;
        })
        .join("")}
    </svg>
  `;
}

function renderPipeline() {
  // Show the latest ETL run so the demo feels operational.
  const latest = state.pipeline;
  el("metric-pipeline").textContent = latest ? `${latest.stage} · ${latest.status}` : "n/a";
  if (!latest) {
    el("pipeline-output").innerHTML = '<div class="row"><strong>Aucun run</strong><span>Lancez le pipeline pour afficher un état.</span></div>';
    return;
  }
  el("pipeline-output").innerHTML = `
    <div class="row">
      <strong>${latest.stage}</strong>
      <span>${latest.run_date} · ${latest.status} · ${latest.row_count} lignes</span>
    </div>
    <div class="row">
      <strong>Dernière mise à jour</strong>
      <span>${new Date(latest.updated_at).toLocaleString()}</span>
    </div>
  `;
}

function renderEvents() {
  renderStack(
    el("events-output"),
    state.events,
    (event) => `
      <strong>${event.event_type}</strong>
      <span>${event.source_id} · ${event.arrondissement_code || "n/a"} · ${new Date(event.event_time).toLocaleString()}</span>
    `
  );
}

async function bootstrap() {
  // Load each API surface independently so one failure does not blank the page.
  if (state.token) {
    el("token-input").value = state.token;
  }

  const results = await Promise.allSettled([
    apiFetch("/catalog/sources"),
    apiFetch("/datamarts/dashboard"),
    apiFetch("/datamarts/timeline"),
    apiFetch("/events/recent"),
    apiFetch("/pipeline/latest"),
  ]);

  const [sourcesRes, dashboardRes, timelineRes, eventsRes, pipelineRes] = results;

  state.sources = sourcesRes.status === "fulfilled" ? sourcesRes.value : [];
  state.dashboard = dashboardRes.status === "fulfilled" ? dashboardRes.value : [];
  state.timeline = timelineRes.status === "fulfilled" ? timelineRes.value : [];
  state.events = eventsRes.status === "fulfilled" ? eventsRes.value : [];
  state.pipeline = pipelineRes.status === "fulfilled" ? pipelineRes.value : null;

  setText(
    "sources-count",
    sourcesRes.status === "fulfilled"
      ? `${state.sources.length} sources cataloguées`
      : `Catalogue indisponible: ${sourcesRes.reason.message}`
  );
  renderDashboard();
  renderTimeline();
  renderPipeline();
  renderEvents();
}

el("source-search").addEventListener("input", renderDashboard);
el("family-filter").addEventListener("change", renderDashboard);
el("token-save").addEventListener("click", () => {
  // Persist the token only in the browser; the backend stays stateless.
  state.token = el("token-input").value.trim();
  localStorage.setItem("ude-token", state.token);
  bootstrap().catch((error) => {
    setText("sources-count", error.message);
    el("pipeline-output").innerHTML = `<div class="row"><strong>Erreur</strong><span>${error.message}</span></div>`;
  });
});

bootstrap().catch((error) => {
  setText("sources-count", error.message);
  el("pipeline-output").innerHTML = `<div class="row"><strong>Erreur</strong><span>${error.message}</span></div>`;
});
