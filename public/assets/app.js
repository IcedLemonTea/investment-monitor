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
  setText("lastRefresh", new Date(snapshot.generated_at).toLocaleString());
  setText("dataSource", `${snapshot.source} / ${snapshot.mode}`);
}

function renderWarnings() {
  const warning = document.getElementById("staleWarning");
  warning.hidden = snapshot.warnings.length === 0;
  warning.textContent = snapshot.warnings.map((item) => item.message).join(" ");
}

function renderAllocation() {
  const chart = document.getElementById("allocationChart");
  chart.innerHTML = "";
  snapshot.positions.forEach((position) => {
    const row = document.createElement("div");
    row.className = "allocation-row";
    row.innerHTML = `
      <span>${position.ticker}</span>
      <div class="bar" aria-hidden="true">
        <i class="actual" style="width: ${position.current_percent * 100}%"></i>
        <i class="target" style="left: ${position.target_percent * 100}%"></i>
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
      <td>${position.name}</td>
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
  historyData.portfolio_value.forEach((point) => {
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

function renderHealth() {
  setText("healthStatus", health.status);
  setText("healthMessage", health.message);
  setText("lastSuccessfulRefresh", new Date(health.last_successful_refresh).toLocaleString());
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
    loadJson("data/latest.example.json"),
    loadJson("data/history.example.json"),
    loadJson("data/health.example.json")
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
    document.getElementById("refreshStatus").textContent =
      "Refresh endpoint is not implemented in v0. This button does not call IBKR.";
  });

  render();
}

init().catch((error) => {
  document.getElementById("refreshStatus").textContent = error.message;
});
