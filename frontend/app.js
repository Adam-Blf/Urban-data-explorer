const apiBase = "http://localhost:8000";

async function loadKpis() {
  const res = await fetch(`${apiBase}/datamarts/arrondissements`);
  const data = await res.json();
  document.getElementById("kpi-output").textContent = JSON.stringify(data, null, 2);
}

async function loadEvents() {
  const res = await fetch(`${apiBase}/events/recent`);
  const data = await res.json();
  document.getElementById("events-output").textContent = JSON.stringify(data, null, 2);
}

loadKpis().catch((e) => {
  document.getElementById("kpi-output").textContent = String(e);
});

loadEvents().catch((e) => {
  document.getElementById("events-output").textContent = String(e);
});

