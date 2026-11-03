let baseScenario, lastResults;
const $ = (id) => document.getElementById(id);

function scenarioFromControls() {
  const scenario = structuredClone(baseScenario);
  scenario.seed = Number($("seed").value);
  scenario.demand[0].rate = Number($("westRate").value);
  scenario.demand[1].rate = Number($("northRate").value);
  return scenario;
}
function download(name, data) {
  const blob = new Blob([JSON.stringify(data, null, 2)], {type:"application/json"});
  const url = URL.createObjectURL(blob), link = Object.assign(document.createElement("a"), {href:url, download:name});
  link.click(); URL.revokeObjectURL(url);
}
function renderNetwork(scenario) {
  const nodes = Object.fromEntries(scenario.nodes.map(n => [n.id,n]));
  const roadSvg = scenario.roads.map(r => `<line class="road ${r.level ? "flyover" : ""}" x1="${nodes[r.from].x}" y1="${nodes[r.from].y}" x2="${nodes[r.to].x}" y2="${nodes[r.to].y}" stroke-width="${7 + r.lanes * 3}"/><text class="label" x="${(nodes[r.from].x+nodes[r.to].x)/2}" y="${(nodes[r.from].y+nodes[r.to].y)/2-10}">${r.id}</text>`).join("");
  const nodeSvg = scenario.nodes.map(n => `<circle class="node" cx="${n.x}" cy="${n.y}" r="7"/><text class="label" x="${n.x+10}" y="${n.y-10}">${n.id}</text>`).join("");
  const signal = scenario.signals.map(s => {const n=nodes[s.node];return `<circle class="signal" cx="${n.x}" cy="${n.y}" r="4"/>`}).join("");
  $("map").innerHTML = roadSvg + nodeSvg + signal;
}
function renderResults(results) {
  const metrics = [["Vehicles generated",results.generated],["Vehicles completed",results.completed],["Average travel time",`${results.average_travel_time} ticks`],["Average waiting time",`${results.average_waiting_time} ticks`],["Maximum queue",results.max_queue_length],["Active now",results.active]];
  $("metrics").innerHTML = metrics.map(([label,value]) => `<article><span>${label}</span><strong>${value}</strong></article>`).join("");
  const rows = Object.entries(results.roads).map(([id,r]) => `<tr><td>${id}</td><td>${Math.round(r.utilisation*100)}%</td><td>${r.max_queue}</td><td>${r.occupancy}</td></tr>`).join("");
  $("roadTable").innerHTML = `<table><thead><tr><th>Road</th><th>Average utilisation</th><th>Max exit queue</th><th>Current occupancy</th></tr></thead><tbody>${rows}</tbody></table>`;
}
async function run() {
  const button=$("run"); button.textContent="Simulating…"; button.disabled=true; $("status").textContent="Running synthetic simulation…";
  try {
    const scenario=scenarioFromControls();
    const response=await fetch("/api/run", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({scenario,ticks:Number($("ticks").value)})});
    const payload=await response.json(); if (!response.ok) throw new Error(payload.error);
    lastResults=payload.results; renderResults(lastResults); renderNetwork(scenario); $("exportResults").disabled=false;
    $("status").textContent=`Completed ${lastResults.tick} ticks: ${lastResults.completed} vehicles completed.`;
  } catch(error) { $("status").textContent=`Simulation could not run: ${error.message}`; alert(`Simulation could not run: ${error.message}`); }
  finally {button.textContent="Run simulation";button.disabled=false;}
}
for (const id of ["westRate","northRate"]) $(id).addEventListener("input", () => $(id === "westRate" ? "westOut" : "northOut").value=$(id).value);
$("run").addEventListener("click",run);
$("reset").addEventListener("click",()=>{ $("seed").value=baseScenario.seed;$("westRate").value=baseScenario.demand[0].rate;$("northRate").value=baseScenario.demand[1].rate;$("westOut").value=$("westRate").value;$("northOut").value=$("northRate").value;$("ticks").value=80;lastResults=null;$("exportResults").disabled=true;$("status").textContent="Controls reset to synthetic demo inputs.";renderNetwork(baseScenario);$("metrics").innerHTML="";$("roadTable").innerHTML="";});
$("exportScenario").addEventListener("click",()=>download("roadflow-scenario.json",scenarioFromControls()));
$("exportResults").addEventListener("click",()=>download("roadflow-results.json",{scenario:scenarioFromControls(),results:lastResults}));
baseScenario=await (await fetch("/api/scenario")).json();renderNetwork(baseScenario);
