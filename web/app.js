let scenarios = [];
let baseScenario, lastResults, lastScenario;
let runToken = 0;
const $ = (id) => document.getElementById(id);
function invalidateRun(message) {
  runToken += 1;
  if (message && $("run").disabled) $("status").textContent = message;
}

function formatDemandLabel(demand) {
  if (demand.label) return demand.label;
  const name = (id) => id.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
  return `${name(demand.origin)} → ${name(demand.destination)} demand / tick`;
}
function scenarioFromControls() {
  const scenario = structuredClone(baseScenario);
  scenario.seed = Number($("seed").value);
  document.querySelectorAll("#demandControls input[type=range]").forEach((input, index) => {
    if (scenario.demand[index]) scenario.demand[index].rate = Number(input.value);
  });
  return scenario;
}
function download(name, data) {
  const blob = new Blob([JSON.stringify(data, null, 2)], {type:"application/json"});
  const url = URL.createObjectURL(blob), link = Object.assign(document.createElement("a"), {href:url, download:name});
  link.click(); URL.revokeObjectURL(url);
}
function roadClass(road) {
  if (road.kind === "ramp") return "ramp";
  if (road.kind === "elevated" || road.level) return "flyover";
  return "";
}
function nodeClass(node) {
  if (node.kind === "elevated") return "elevated-node";
  if (node.kind === "ramp") return "ramp-node";
  return "";
}
function roadLabelOffset(road) {
  if (road.kind === "ramp") return 16;
  if (road.kind === "elevated" || road.level) return -12;
  return -10;
}
function nodeLabelOffset(node) {
  if (node.kind === "elevated") return {dx:13, dy:20};
  if (node.kind === "ramp") return {dx:10, dy:16};
  return {dx:10, dy:-10};
}
function renderNetwork(scenario) {
  const nodes = Object.fromEntries(scenario.nodes.map(n => [n.id,n]));
  const roadSvg = scenario.roads.map(r => {
    const from = nodes[r.from], to = nodes[r.to];
    return `<line class="road ${roadClass(r)}" data-road="${r.id}" x1="${from.x}" y1="${from.y}" x2="${to.x}" y2="${to.y}" stroke-width="${7 + r.lanes * 3}"/><text class="label" x="${(from.x+to.x)/2}" y="${(from.y+to.y)/2+roadLabelOffset(r)}">${r.id}</text>`;
  }).join("");
  const nodeSvg = scenario.nodes.map(n => {
    const offset = nodeLabelOffset(n);
    return `<circle class="node ${nodeClass(n)}" data-node="${n.id}" cx="${n.x}" cy="${n.y}" r="${n.kind === "elevated" ? 11 : 7}"/><text class="label" x="${n.x+offset.dx}" y="${n.y+offset.dy}">${n.id}</text>`;
  }).join("");
  const signalSvg = (scenario.signals || []).map(s => {
    const node = nodes[s.node];
    return `<circle class="signal" cx="${node.x}" cy="${node.y}" r="4"/>`;
  }).join("");
  $("map").innerHTML = roadSvg + nodeSvg + signalSvg;
}
function renderDemandControls(scenario) {
  $("demandControls").innerHTML = scenario.demand.map((demand, index) => {
    const id = `demand-${index}`;
    return `<label>${formatDemandLabel(demand)}<input id="${id}" type="range" min="0" max="1" step=".01" value="${demand.rate}"><output id="${id}-out">${Number(demand.rate).toFixed(2)}</output></label>`;
  }).join("");
  document.querySelectorAll("#demandControls input[type=range]").forEach(input => {
    input.addEventListener("input", () => {
      $(`${input.id}-out`).value = input.value;
      invalidateRun("Controls changed; previous run discarded.");
    });
  });
}
function renderResults(results) {
  const metrics = [["Vehicles generated",results.generated],["Vehicles completed",results.completed],["Average travel time",`${results.average_travel_time} ticks`],["Average waiting time",`${results.average_waiting_time} ticks`],["Maximum queue",results.max_queue_length],["Active now",results.active]];
  $("metrics").innerHTML = metrics.map(([label,value]) => `<article><span>${label}</span><strong>${value}</strong></article>`).join("");
  const rows = Object.entries(results.roads).map(([id,r]) => `<tr><td>${id}</td><td>${Math.round(r.utilisation*100)}%</td><td>${r.max_queue}</td><td>${r.occupancy}</td></tr>`).join("");
  $("roadTable").innerHTML = `<table><thead><tr><th>Road</th><th>Average utilisation</th><th>Max exit queue</th><th>Current occupancy</th></tr></thead><tbody>${rows}</tbody></table>`;
}
function activateScenario(scenario, statusText) {
  invalidateRun();
  baseScenario = scenario;
  $("scenario").value = scenario.name;
  $("seed").value = scenario.seed;
  $("ticks").value = 80;
  $("scenarioNote").textContent = scenario.description || "";
  renderDemandControls(scenario);
  renderNetwork(scenario);
  lastResults = null;
  lastScenario = null;
  $("exportResults").disabled = true;
  $("metrics").innerHTML = "";
  $("roadTable").innerHTML = "";
  $("status").textContent = statusText || `Loaded ${scenario.name}.`;
}
async function run() {
  const token=++runToken;
  const button=$("run"); button.textContent="Simulating…"; button.disabled=true; $("status").textContent="Running synthetic simulation…";
  try {
    const scenario=scenarioFromControls();
    const response=await fetch("/api/run", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({scenario,ticks:Number($("ticks").value)})});
    const payload=await response.json();
    if (token !== runToken) return;
    if (!response.ok) throw new Error(payload.error);
    lastResults=payload.results; lastScenario=scenario; renderResults(lastResults); renderNetwork(scenario); $("exportResults").disabled=false;
    $("status").textContent=`Completed ${lastResults.tick} ticks: ${lastResults.completed} vehicles completed.`;
  } catch(error) { if (token !== runToken) return; $("status").textContent=`Simulation could not run: ${error.message}`; alert(`Simulation could not run: ${error.message}`); }
  finally {button.textContent="Run simulation";button.disabled=false;}
}
$("scenario").addEventListener("change", () => {
  const scenario = scenarios.find(item => item.name === $("scenario").value);
  if (scenario) activateScenario(scenario);
});
$("seed").addEventListener("input", () => invalidateRun("Controls changed; previous run discarded."));
$("ticks").addEventListener("input", () => invalidateRun("Controls changed; previous run discarded."));
$("run").addEventListener("click",run);
$("reset").addEventListener("click",() => activateScenario(baseScenario, "Controls reset to scenario defaults."));
$("exportScenario").addEventListener("click",()=>download("roadflow-scenario.json",scenarioFromControls()));
$("exportResults").addEventListener("click",()=>download("roadflow-results.json",{scenario:lastScenario,results:lastResults}));
async function loadScenarioCatalog() {
  try {
    const response = await fetch("/api/scenarios");
    if (!response.ok) throw new Error("catalog unavailable");
    const data = await response.json();
    if (!Array.isArray(data) || data.length === 0) throw new Error("catalog unavailable");
    return data;
  } catch {
    const response = await fetch("/api/scenario");
    if (!response.ok) throw new Error("scenario unavailable");
    return [await response.json()];
  }
}
try {
  scenarios = await loadScenarioCatalog();
  $("scenario").innerHTML = scenarios.map(scenario => `<option value="${scenario.name}">${scenario.name}</option>`).join("");
  activateScenario(scenarios[0], "Ready with synthetic demo inputs.");
} catch (error) {
  $("status").textContent = `Scenario could not load: ${error.message}`;
}
