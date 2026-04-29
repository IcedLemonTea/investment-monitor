const snapshot = {
  schema_version: "1.0",
  source: "mock",
  mode: "example",
  generated_at: "2026-04-29T14:00:00Z",
  base_currency: "USD",
  display_currency: "MYR",
  fx: { USD_MYR: 4.75, source: "manual_config" },
  account: {
    account_id: "EXAMPLE",
    net_liquidation: 100000,
    daily_pnl: 250,
    unrealized_pnl: 5000,
    realized_pnl: 100,
    margin_value: 0,
    excess_liquidity: 100000
  },
  positions: [
    { ticker: "QLD", name: "ProShares Ultra QQQ", units: 632.83, unit_price: 79, market_value: 50000, current_percent: 0.5, target_percent: 0.5, drift_percent: 0, unrealized_pnl: 2500, daily_pnl: 150, currency: "USD" },
    { ticker: "TQQQ", name: "ProShares UltraPro QQQ", units: 166.67, unit_price: 60, market_value: 10000, current_percent: 0.1, target_percent: 0.1, drift_percent: 0, unrealized_pnl: 800, daily_pnl: 40, currency: "USD" },
    { ticker: "AVUV", name: "Avantis U.S. Small Cap Value ETF", units: 250, unit_price: 80, market_value: 20000, current_percent: 0.2, target_percent: 0.2, drift_percent: 0, unrealized_pnl: 900, daily_pnl: 25, currency: "USD" },
    { ticker: "AVDV", name: "Avantis International Small Cap Value ETF", units: 200, unit_price: 50, market_value: 10000, current_percent: 0.1, target_percent: 0.1, drift_percent: 0, unrealized_pnl: 400, daily_pnl: 20, currency: "USD" },
    { ticker: "QMOM", name: "Alpha Architect U.S. Quantitative Momentum ETF", units: 100, unit_price: 100, market_value: 10000, current_percent: 0.1, target_percent: 0.1, drift_percent: 0, unrealized_pnl: 400, daily_pnl: 15, currency: "USD" }
  ],
  warnings: [{ code: "STALE_DATA", message: "Example snapshot only. No live IBKR calls are implemented." }]
};

let displayCurrency = "USD";

const percent = new Intl.NumberFormat("en-US", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2
});

function money(value) {
  const converted = displayCurrency === "MYR" ? value * snapshot.fx.USD_MYR : value;
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: displayCurrency
  }).format(converted);
}

function setText(id, value) {
  document.getElementById(id).textContent = value;
}

function renderSummary() {
  setText("netLiquidation", money(snapshot.account.net_liquidation));
  setText("dailyPnl", money(snapshot.account.daily_pnl));
  setText("unrealizedPnl", money(snapshot.account.unrealized_pnl));
  setText("realizedPnl", money(snapshot.account.realized_pnl));
  setText("marginValue", money(snapshot.account.margin_value));
  setText("lastRefresh", new Date(snapshot.generated_at).toLocaleString());
  setText("dataSource", snapshot.source);
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
        <i class="target" style="width: ${position.target_percent * 100}%"></i>
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
      <td>${percent.format(position.drift_percent * 100)}%</td>
      <td>${money(position.unrealized_pnl)}</td>
      <td>${money(position.daily_pnl)}</td>
      <td>${position.currency}</td>
    `;
    body.appendChild(row);
  });
}

function renderDrift() {
  const body = document.getElementById("driftBody");
  body.innerHTML = "";
  snapshot.positions.forEach((position) => {
    const targetValue = snapshot.account.net_liquidation * position.target_percent;
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${position.ticker}</td>
      <td>${percent.format(position.target_percent * 100)}%</td>
      <td>${percent.format(position.current_percent * 100)}%</td>
      <td>${percent.format(position.drift_percent * 100)}%</td>
      <td>${money(targetValue - position.market_value)}</td>
    `;
    body.appendChild(row);
  });
}

function render() {
  renderSummary();
  renderWarnings();
  renderAllocation();
  renderPositions();
  renderDrift();
}

document.getElementById("currencyToggle").addEventListener("change", (event) => {
  displayCurrency = event.target.checked ? "MYR" : "USD";
  render();
});

document.getElementById("refreshButton").addEventListener("click", () => {
  document.getElementById("refreshStatus").textContent = "Refresh endpoint is not implemented in v0.";
});

render();
