let snapshot;
let historyData;
let health;
let displayCurrency = "USD";
let theme = localStorage.getItem("investment-monitor-theme") || "dark";

const percent = new Intl.NumberFormat("en-US", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2
});

async function loadJson(path) {
  const response = await fetch(path, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`Failed to load ${path}: ${response.status}`);
  }
  return response.json();
}

async function loadJsonWithFallback(primaryPath, fallbackPath) {
  try {
    return await loadJson(primaryPath);
  } catch {
    return loadJson(fallbackPath);
  }
}

function money(value) {
  const rate = snapshot?.fx?.USD_MYR;
  const converted = displayCurrency === "MYR" && rate ? value * rate : value;
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: displayCurrency
  }).format(converted);
}

function setText(id, value) {
  document.getElementById(id).textContent = value;
}

function signedClass(value) {
  if (value > 0) return "positive";
  if (value < 0) return "negative";
  return "";
}

function renderSummary() {
  setText("netLiquidation", money(snapshot.account.net_liquidation));
  setText("dailyPnl", money(snapshot.account.daily_pnl));
  setText("unrealizedPnl", money(snapshot.account.unrealized_pnl));
  setText("realizedPnl", money(snapshot.account.realized_pnl));
  setText("marginValue", money(snapshot.account.margin_value));
  setText("totalMarketValue", money(snapshot.account.total_market_value));
  setText("lastRefresh", formatLocalDateTime(snapshot.generated_at));
  setText("dataSource", `${snapshot.source} / ${snapshot.mode}`);
}

function renderWarnings() {
  const warning = document.getElementById("staleWarning");
  const visibleWarnings = snapshot.warnings.filter((item) => item.code !== "FLEX_STATEMENT_DATA");
  warning.hidden = visibleWarnings.length === 0;
  warning.textContent = visibleWarnings.map((item) => item.message).join(" ");
}

function renderAllocation() {
  const chart = document.getElementById("allocationChart");
  chart.innerHTML = "";
  const maxAllocation = Math.max(
    ...snapshot.positions.flatMap((position) => [
      position.current_percent,
      position.target_percent
    ]),
    0.01
  );
  snapshot.positions.forEach((position) => {
    const actualWidth = (position.current_percent / maxAllocation) * 100;
    const targetLeft = Math.min((position.target_percent / maxAllocation) * 100, 100);
    const row = document.createElement("div");
    row.className = "allocation-row";
    row.innerHTML = `
      <span>${position.ticker}</span>
      <div class="bar" aria-hidden="true">
        <i class="actual" style="width: ${actualWidth}%"></i>
        <i class="target" style="left: ${targetLeft}%"></i>
      </div>
      <strong>${percent.format(position.current_percent * 100)}%</strong>
    `;
    chart.appendChild(row);
  });
}

function renderPositions() {
  const body = document.getElementById("positionsBody");
  body.innerHTML = "";
  snapshot.positions.forEach((position) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${position.ticker}</td>
      <td class="truncate" title="${escapeHtml(position.name)}">${position.name}</td>
      <td>${percent.format(position.units)}</td>
      <td>${money(position.unit_price)}</td>
      <td>${money(position.market_value)}</td>
      <td>${percent.format(position.current_percent * 100)}%</td>
      <td>${percent.format(position.target_percent * 100)}%</td>
      <td class="${signedClass(position.drift_percent)}">${percent.format(position.drift_percent * 100)}%</td>
      <td class="${signedClass(position.unrealized_pnl)}">${money(position.unrealized_pnl)}</td>
      <td class="${signedClass(position.daily_pnl)}">${money(position.daily_pnl)}</td>
      <td>${position.currency}</td>
    `;
    body.appendChild(row);
  });
}

function renderDrift() {
  const body = document.getElementById("driftBody");
  body.innerHTML = "";
  snapshot.positions.forEach((position) => {
    const targetValue = snapshot.account.total_market_value * position.target_percent;
    const rebalanceValue = targetValue - position.market_value;
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${position.ticker}</td>
      <td>${percent.format(position.target_percent * 100)}%</td>
      <td>${percent.format(position.current_percent * 100)}%</td>
      <td class="${signedClass(position.drift_percent)}">${percent.format(position.drift_percent * 100)}%</td>
      <td class="${signedClass(rebalanceValue)}">${money(rebalanceValue)}</td>
    `;
    body.appendChild(row);
  });
}

function renderHistory() {
  const valueBody = document.getElementById("historyBody");
  valueBody.innerHTML = "";
  const points = historyData.portfolio_value;
  const pnlPoints = historyData.daily_pnl;

  setText("historySummary", `${points.length} daily points from local history`);
  renderMiniChart("portfolioValueChart", points.map((point) => point.net_liquidation));
  renderMiniChart("dailyPnlChart", pnlPoints.map((point) => point.value), true);
  setText("portfolioValueRange", rangeText(points.map((point) => point.net_liquidation)));
  setText("dailyPnlRange", rangeText(pnlPoints.map((point) => point.value)));

  points.slice(-30).forEach((point) => {
    const pnlPoint = historyData.daily_pnl.find((item) => item.date === point.date);
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${point.date}</td>
      <td>${money(point.net_liquidation)}</td>
      <td class="${signedClass(pnlPoint?.value ?? 0)}">${money(pnlPoint?.value ?? 0)}</td>
    `;
    valueBody.appendChild(row);
  });
}

function renderMiniChart(id, values, signed = false) {
  const chart = document.getElementById(id);
  chart.innerHTML = "";
  if (values.length === 0) return;

  const visibleValues = values.slice(-85);
  const min = Math.min(...visibleValues);
  const max = Math.max(...visibleValues);
  const span = max - min || 1;
  visibleValues.forEach((value) => {
    const bar = document.createElement("i");
    const height = signed
      ? Math.max(4, (Math.abs(value) / Math.max(Math.abs(min), Math.abs(max), 1)) * 100)
      : Math.max(4, ((value - min) / span) * 100);
    bar.style.height = `${height}%`;
    if (signed) {
      bar.className = value < 0 ? "negative-bar" : "positive-bar";
    }
    chart.appendChild(bar);
  });
}

function rangeText(values) {
  if (values.length === 0) return "--";
  return `${money(Math.min(...values))} - ${money(Math.max(...values))}`;
}

function renderHealth() {
  setText("healthStatus", health.status);
  setText("healthMessage", health.message);
  setText("lastSuccessfulRefresh", formatLocalDateTime(health.last_successful_refresh));
}

function formatLocalDateTime(value) {
  return new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
    timeZoneName: "short"
  }).format(new Date(value));
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll('"', "&quot;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function render() {
  document.body.dataset.theme = theme;
  renderSummary();
  renderWarnings();
  renderAllocation();
  renderPositions();
  renderDrift();
  renderHistory();
  renderHealth();
}

async function init() {
  [snapshot, historyData, health] = await Promise.all([
    loadJsonWithFallback("data/latest.json", "data/latest.example.json"),
    loadJsonWithFallback("data/history.json", "data/history.example.json"),
    loadJsonWithFallback("data/health.json", "data/health.example.json")
  ]);

  const themeToggle = document.getElementById("themeToggle");
  themeToggle.checked = theme === "dark";
  document.body.dataset.theme = theme;
  themeToggle.addEventListener("change", (event) => {
    theme = event.target.checked ? "dark" : "light";
    localStorage.setItem("investment-monitor-theme", theme);
    document.body.dataset.theme = theme;
  });

  const currencyToggle = document.getElementById("currencyToggle");
  currencyToggle.disabled = !snapshot.fx?.USD_MYR;
  currencyToggle.addEventListener("change", (event) => {
    displayCurrency = event.target.checked ? "MYR" : "USD";
    render();
  });

  document.getElementById("refreshButton").addEventListener("click", () => {
    refreshNow();
  });

  render();
}

async function refreshNow() {
  const status = document.getElementById("refreshStatus");
  const button = document.getElementById("refreshButton");
  button.disabled = true;
  status.textContent = "Refreshing local snapshot...";
  try {
    const response = await fetch("/api/refresh-now", { method: "POST" });
    if (!response.ok) {
      throw new Error(`Refresh failed: ${response.status}`);
    }
    await response.json();
    [snapshot, health] = await Promise.all([
      loadJson("data/latest.json"),
      loadJson("data/health.json")
    ]);
    render();
    status.textContent = `${snapshot.source.toUpperCase()} refresh complete.`;
  } catch (error) {
    status.textContent = error.message;
  } finally {
    button.disabled = false;
  }
}

init().catch((error) => {
  document.getElementById("refreshStatus").textContent = error.message;
});
