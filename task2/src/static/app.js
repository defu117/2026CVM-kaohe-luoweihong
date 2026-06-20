const state = {
  samples: [],
};

const $ = (id) => document.getElementById(id);

function formatBytes(value) {
  if (!value) return "0 B";
  const units = ["B", "KB", "MB", "GB"];
  let size = value;
  let index = 0;
  while (size >= 1024 && index < units.length - 1) {
    size /= 1024;
    index += 1;
  }
  return `${size.toFixed(index === 0 ? 0 : 1)} ${units[index]}`;
}

function toInputValue(displayTime) {
  if (!displayTime) return "";
  return displayTime.replace(" ", "T");
}

function showMessage(text, kind = "info") {
  const node = $("message");
  node.textContent = text;
  node.className = `message ${kind}`;
}

async function fetchJson(url, options) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || `HTTP ${response.status}`);
  }
  return data;
}

async function refreshStatus() {
  const status = await fetchJson("/api/status");
  $("collectorState").textContent = status.collector_running ? "Running" : "Stopped";
  $("collectorState").className = status.collector_running ? "ok" : "warn";
  $("sampleCount").textContent = status.sample_count;
  $("windowSeconds").textContent = `${status.window_seconds}s`;
  $("dataSize").textContent = formatBytes(status.disk.data_bytes);
  $("subtitle").textContent = `${status.perf_event} / ${status.perf_scope} / ${status.now}`;

  const samples = await fetchJson("/api/samples?hours=24");
  state.samples = samples;
  renderTimeline(samples);
  setDefaultRange(samples);
}

function renderTimeline(samples) {
  const timeline = $("timeline");
  timeline.innerHTML = "";

  if (!samples.length) {
    timeline.innerHTML = '<div class="empty">No samples yet</div>';
    return;
  }

  for (const sample of samples.slice(-40).reverse()) {
    const item = document.createElement("button");
    item.type = "button";
    item.className = `sample ${sample.status}`;
    item.innerHTML = `
      <span>${sample.start}</span>
      <span>${sample.end}</span>
      <small>${sample.status} · ${formatBytes(sample.size_bytes)}</small>
    `;
    item.addEventListener("click", () => {
      $("startTime").value = toInputValue(sample.start);
      $("endTime").value = toInputValue(sample.end);
    });
    timeline.appendChild(item);
  }
}

function setDefaultRange(samples) {
  if ($("startTime").value || $("endTime").value || !samples.length) return;

  const okSamples = samples.filter((sample) => sample.status === "ok");
  const last = okSamples[okSamples.length - 1];
  if (!last) return;

  $("startTime").value = toInputValue(last.start);
  $("endTime").value = toInputValue(last.end);
}

async function generateFlameGraph() {
  const start = $("startTime").value;
  const end = $("endTime").value;

  if (!start || !end) {
    showMessage("Select a start and end time.", "error");
    return;
  }

  $("generateBtn").disabled = true;
  showMessage("Generating flame graph...");

  try {
    const result = await fetchJson("/api/flamegraph", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({start, end}),
    });
    $("svgFrame").src = result.url;
    $("openSvg").href = result.url;
    showMessage(`Generated from ${result.sample_count} sample window(s).`, "ok");
  } catch (error) {
    showMessage(error.message, "error");
  } finally {
    $("generateBtn").disabled = false;
  }
}

async function controlCollector(action) {
  await fetchJson(`/api/collector/${action}`, {method: "POST"});
  await refreshStatus();
}

$("refreshBtn").addEventListener("click", () => refreshStatus().catch((error) => showMessage(error.message, "error")));
$("generateBtn").addEventListener("click", generateFlameGraph);
$("startBtn").addEventListener("click", () => controlCollector("start").catch((error) => showMessage(error.message, "error")));
$("stopBtn").addEventListener("click", () => controlCollector("stop").catch((error) => showMessage(error.message, "error")));

refreshStatus().catch((error) => showMessage(error.message, "error"));
setInterval(() => refreshStatus().catch(() => {}), 10000);

