let snapshot;
let historyData;
let health;
let filteredPositions = [];
let displayCurrency = "USD";
let theme = localStorage.getItem("investment-monitor-theme") || "dark";
let activeRange = "ALL";
let activeBenchmark = "portfolio";
const tinyHoldingThreshold = 0.015;
const allocationMaxRows = 8;

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
  const element = document.getElementById(id);
  if (element) {
    element.textContent = value;
  }
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
  setText("totalMarketValue", money(snapshot.account.total_market_value));
  setText("lastRefresh", formatLocalDateTime(snapshot.generated_at));
  setText("dataSource", `${snapshot.source} / ${snapshot.mode}`);
  setText("sidebarSource", `${snapshot.source} / ${snapshot.mode}`);
  setText("sidebarRefresh", formatLocalDateTime(snapshot.generated_at));
}

function updateThemeButtons() {
  const lightButton = document.getElementById("lightButton");
  const darkButton = document.getElementById("darkButton");
  const themePill = document.querySelector(".theme-pill");
  if (!lightButton || !darkButton || !themePill) return;
  lightButton.classList.toggle("active", theme === "light");
  darkButton.classList.toggle("active", theme === "dark");
  themePill.dataset.active = theme === "dark" ? "right" : "left";
  lightButton.setAttribute("aria-pressed", String(theme === "light"));
  darkButton.setAttribute("aria-pressed", String(theme === "dark"));
}

function renderWarnings() {
  const warning = document.getElementById("staleWarning");
  const visibleWarnings = snapshot.warnings.filter((item) => item.code !== "FLEX_STATEMENT_DATA");
  warning.hidden = visibleWarnings.length === 0;
  warning.textContent = visibleWarnings.map((item) => item.message).join(" ");
}

function renderAllocation() {
  const chart = document.getElementById("allocationBars");
  chart.innerHTML = "";

  const rows = compactAllocationRows(filteredPositions);
  const maxAllocation = Math.max(
    ...rows.flatMap((position) => [position.current_percent, position.target_percent]),
    0.01
  );

  rows.forEach((position) => {
    const actualWidth = Math.max(2, (position.current_percent / maxAllocation) * 100);
    const targetLeft = Math.min((position.target_percent / maxAllocation) * 100, 100);
    const row = document.createElement("div");
    row.className = "allocation-bar";
    row.innerHTML = `
      <strong title="${escapeHtml(position.name)}">${escapeHtml(position.ticker)}</strong>
      <div class="allocation-track" title="${escapeHtml(position.name)}">
        <i class="allocation-fill" style="width: ${actualWidth}%"></i>
        <i class="allocation-target" style="left: ${targetLeft}%"></i>
      </div>
      <span>${percent.format(position.current_percent * 100)}%</span>
    `;
    chart.appendChild(row);
  });

  setText("allocationCount", `${filteredPositions.length} holdings`);
}

function compactAllocationRows(positions) {
  const sorted = [...positions].sort((a, b) => b.current_percent - a.current_percent);
  const shouldAggregate = sorted.length > allocationMaxRows;
  const rows = [];
  const tinyRows = [];

  sorted.forEach((position) => {
    if (shouldAggregate && position.current_percent < tinyHoldingThreshold) {
      tinyRows.push(position);
    } else {
      rows.push(position);
    }
  });

  while (rows.length > allocationMaxRows - 1) {
    tinyRows.push(rows.pop());
  }

  if (tinyRows.length === 0) return rows;

  const aggregate = tinyRows.reduce(
    (total, position) => {
      total.market_value += position.market_value;
      total.current_percent += position.current_percent;
      total.target_percent += position.target_percent;
      total.drift_percent += position.drift_percent;
      return total;
    },
    {
      ticker: "Other",
      name: tinyRows.map((position) => position.ticker).join(", "),
      market_value: 0,
      current_percent: 0,
      target_percent: 0,
      drift_percent: 0
    }
  );

  return [...rows, aggregate].sort((a, b) => b.current_percent - a.current_percent);
}

function renderPositions() {
  const body = document.getElementById("positionsBody");
  body.innerHTML = "";
  filteredPositions.forEach((position) => {
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
  setText("positionCount", `${filteredPositions.length} shown`);
}

function renderDrift() {
  const body = document.getElementById("driftBody");
  body.innerHTML = "";
  filteredPositions.forEach((position) => {
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

function renderTopCards() {
  const topPositions = [...snapshot.positions]
    .sort((a, b) => b.market_value - a.market_value)
    .slice(0, 10);
  renderPortfolioHeatmap("topPositionsList", topPositions);

  const topDrift = [...snapshot.positions]
    .sort((a, b) => Math.abs(b.drift_percent) - Math.abs(a.drift_percent))
    .slice(0, 4);
  renderStackList("topDriftList", topDrift, (position) => ({
    avatar: position.ticker.slice(0, 2),
    title: `${position.ticker} drift`,
    subtitle: `${percent.format(position.current_percent * 100)}% current`,
    value: `${percent.format(position.drift_percent * 100)}%`,
    className: signedClass(position.drift_percent)
  }));

  const alignment = targetAlignment(snapshot.positions);
  setText("targetAlignment", `${Math.round(alignment * 100)}%`);
  document.getElementById("targetGauge").style.setProperty("--gauge", `${alignment * 360}deg`);
}

function renderPortfolioHeatmap(id, rows) {
  const list = document.getElementById(id);
  list.innerHTML = "";

  const maxValue = Math.max(...rows.map((position) => position.market_value), 1);
  const maxPnl = Math.max(...rows.map((position) => Math.abs(position.unrealized_pnl || position.daily_pnl || 0)), 1);
  rows.forEach((position, index) => {
    const share = Math.max(position.current_percent, position.market_value / maxValue / 10);
    const columnSpan = Math.max(1, Math.min(6, Math.round(share * 12)));
    const rowSpan = Math.max(1, Math.min(3, Math.round(share * 7)));
    const pnl = position.daily_pnl || position.unrealized_pnl || 0;
    const pnlClass = signedClass(pnl);
    const intensity = Math.min(0.72, 0.16 + Math.abs(pnl) / maxPnl * 0.56);
    const color = pnl < 0 ? "var(--danger)" : "var(--success)";
    const hideDetails = columnSpan < 2 || rowSpan < 2;
    const tile = document.createElement("div");
    tile.className = `heatmap-tile ${pnlClass}${hideDetails ? " heatmap-tile-compact" : ""}`;
    tile.style.cssText = [
      `grid-column:span ${index === 0 ? Math.max(3, columnSpan) : columnSpan}`,
      `grid-row:span ${index === 0 ? Math.max(2, rowSpan) : rowSpan}`,
      `background: color-mix(in srgb, ${color} ${Math.round(intensity * 100)}%, var(--panel-raised))`
    ].join(";");
    tile.title = `${position.ticker} - ${position.name} - ${money(position.market_value)} - P&L ${money(pnl)}`;
    tile.innerHTML = `
      <strong>${escapeHtml(position.ticker)}</strong>
      <span>${percent.format(position.current_percent * 100)}% / ${money(position.market_value)}</span>
    `;
    list.appendChild(tile);
  });
}

function renderStackList(id, rows, mapper) {
  const list = document.getElementById(id);
  list.innerHTML = "";
  rows.forEach((row) => {
    const item = mapper(row);
    const element = document.createElement("div");
    element.className = "stack-item";
    element.innerHTML = `
      <div class="avatar">${escapeHtml(item.avatar)}</div>
      <div>
        <strong>${escapeHtml(item.title)}</strong>
        <span title="${escapeHtml(item.subtitle)}">${escapeHtml(item.subtitle)}</span>
      </div>
      <strong class="${item.className || ""}">${escapeHtml(item.value)}</strong>
    `;
    list.appendChild(element);
  });
}

function renderHistory() {
  const valueBody = document.getElementById("historyBody");
  valueBody.innerHTML = "";
  const points = filterHistoryPoints(historyData.portfolio_value);
  const pnlPoints = historyData.daily_pnl.filter((point) => points.some((item) => item.date === point.date));

  setText("historySummary", `${points.length} ${activeRange} points from local history`);
  renderLineAreaChart("portfolioValueChart", points.map((point) => point.net_liquidation), {
    labelMin: money(Math.min(...points.map((point) => point.net_liquidation))),
    labelMax: money(Math.max(...points.map((point) => point.net_liquidation)))
  });
  renderPnlChart("dailyPnlChart", pnlPoints.map((point) => point.value));
  renderDrawdown(points);
  setText("portfolioValueRange", rangeText(points.map((point) => point.net_liquidation)));
  setText("dailyPnlRange", rangeText(pnlPoints.map((point) => point.value)));

  points.slice(-14).forEach((point) => {
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

function filterHistoryPoints(points) {
  if (activeRange === "ALL" || points.length === 0) return points;
  const latest = new Date(`${points.at(-1).date}T00:00:00`);
  const start = new Date(latest);
  if (activeRange === "1Y") start.setFullYear(start.getFullYear() - 1);
  if (activeRange === "5Y") start.setFullYear(start.getFullYear() - 5);
  if (activeRange === "YTD") {
    start.setMonth(0, 1);
  }
  if (activeRange === "MTD") {
    start.setDate(1);
  }
  if (activeRange === "WTD") {
    start.setDate(start.getDate() - start.getDay());
  }
  if (activeRange === "1D") {
    return points.slice(-1);
  }
  return points.filter((point) => new Date(`${point.date}T00:00:00`) >= start);
}

function renderLineAreaChart(id, values, labels = {}) {
  const chart = document.getElementById(id);
  chart.innerHTML = "";
  if (values.length === 0) return;

  const visibleValues = values.slice(-85);
  const min = Math.min(...visibleValues);
  const max = Math.max(...visibleValues);
  const span = max - min || 1;
  const width = 520;
  const height = 180;
  const padding = { top: 16, right: 14, bottom: 24, left: 72 };
  const points = visibleValues.map((value, index) => {
    const x = padding.left + (index / Math.max(visibleValues.length - 1, 1)) * (width - padding.left - padding.right);
    const y = height - padding.bottom - ((value - min) / span) * (height - padding.top - padding.bottom);
    return { x, y };
  });
  const line = points.map((point) => `${point.x.toFixed(2)},${point.y.toFixed(2)}`).join(" ");
  const area = [
    `${padding.left},${height - padding.bottom}`,
    ...points.map((point) => `${point.x.toFixed(2)},${point.y.toFixed(2)}`),
    `${width - padding.right},${height - padding.bottom}`
  ].join(" ");

  chart.style.display = "block";
  chart.style.padding = "0";
  chart.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Portfolio value trend" style="display:block;width:100%;height:100%;">
      <line x1="${padding.left}" y1="${padding.top}" x2="${padding.left}" y2="${height - padding.bottom}" stroke="var(--line)" stroke-width="1"></line>
      <line x1="${padding.left}" y1="${height - padding.bottom}" x2="${width - padding.right}" y2="${height - padding.bottom}" stroke="var(--line)" stroke-width="1"></line>
      <text x="${padding.left - 8}" y="${padding.top + 4}" text-anchor="end" fill="var(--muted)" font-size="11">${escapeHtml(labels.labelMax || money(max))}</text>
      <text x="${padding.left - 8}" y="${height - padding.bottom + 4}" text-anchor="end" fill="var(--muted)" font-size="11">${escapeHtml(labels.labelMin || money(min))}</text>
      <polygon points="${area}" fill="var(--accent)" opacity="0.22"></polygon>
      <polyline points="${line}" fill="none" stroke="var(--accent-strong)" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"></polyline>
    </svg>
  `;
}

function renderPnlChart(id, values) {
  const chart = document.getElementById(id);
  chart.innerHTML = "";
  if (values.length === 0) return;

  const visibleValues = values.slice(-85);
  const width = 380;
  const height = 180;
  const padding = { top: 16, right: 12, bottom: 24, left: 70 };
  const maxAbs = Math.max(...visibleValues.map((value) => Math.abs(value)), 1);
  const zeroY = padding.top + (height - padding.top - padding.bottom) / 2;
  const innerWidth = width - padding.left - padding.right;
  const barWidth = Math.max(1.5, innerWidth / visibleValues.length * 0.68);
  const bars = visibleValues.map((value, index) => {
    const x = padding.left + (index / visibleValues.length) * innerWidth;
    const heightValue = Math.abs(value) / maxAbs * ((height - padding.top - padding.bottom) / 2);
    const y = value >= 0 ? zeroY - heightValue : zeroY;
    const color = value >= 0 ? "var(--success)" : "var(--danger)";
    return `<rect x="${x.toFixed(2)}" y="${y.toFixed(2)}" width="${barWidth.toFixed(2)}" height="${Math.max(1, heightValue).toFixed(2)}" rx="1.5" fill="${color}"></rect>`;
  }).join("");

  chart.style.display = "block";
  chart.style.padding = "0";
  chart.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Daily P&L bars" style="display:block;width:100%;height:100%;">
      <line x1="${padding.left}" y1="${padding.top}" x2="${padding.left}" y2="${height - padding.bottom}" stroke="var(--line)" stroke-width="1"></line>
      <line x1="${padding.left}" y1="${zeroY}" x2="${width - padding.right}" y2="${zeroY}" stroke="var(--line)" stroke-width="1.4"></line>
      <text x="${padding.left - 8}" y="${padding.top + 4}" text-anchor="end" fill="var(--muted)" font-size="11">${escapeHtml(money(maxAbs))}</text>
      <text x="${padding.left - 8}" y="${height - padding.bottom + 4}" text-anchor="end" fill="var(--muted)" font-size="11">${escapeHtml(money(-maxAbs))}</text>
      ${bars}
    </svg>
  `;
}

function renderDrawdown(points) {
  const drawdownChart = document.getElementById("drawdownChart");
  if (!drawdownChart) return;

  const drawdowns = calculateDrawdowns(points.map((point) => point.net_liquidation));
  renderDrawdownChart("drawdownChart", drawdowns);

  const maxDrawdown = Math.min(...drawdowns, 0);
  setText("drawdownRange", `${percent.format(maxDrawdown * 100)}% max drawdown`);
  setText("maxDrawdown", `${percent.format(maxDrawdown * 100)}%`);
}

function renderDrawdownChart(id, values) {
  const chart = document.getElementById(id);
  chart.innerHTML = "";
  if (values.length === 0) return;

  const visibleValues = values.slice(-85);
  const min = Math.min(...visibleValues, 0);
  const floor = Math.min(-0.01, Math.floor(min * 100 / 5) * 5 / 100);
  const width = 760;
  const height = 130;
  const padding = { top: 14, right: 12, bottom: 24, left: 70 };
  const innerWidth = width - padding.left - padding.right;
  const innerHeight = height - padding.top - padding.bottom;
  const points = visibleValues.map((value, index) => {
    const x = padding.left + (index / Math.max(visibleValues.length - 1, 1)) * innerWidth;
    const y = padding.top + (value / floor) * innerHeight;
    return { x, y };
  });
  const line = points.map((point) => `${point.x.toFixed(2)},${point.y.toFixed(2)}`).join(" ");
  const area = [
    `${padding.left},${padding.top}`,
    ...points.map((point) => `${point.x.toFixed(2)},${point.y.toFixed(2)}`),
    `${width - padding.right},${padding.top}`
  ].join(" ");

  chart.style.display = "block";
  chart.style.padding = "0";
  chart.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="Drawdown chart" style="display:block;width:100%;height:100%;">
      <line x1="${padding.left}" y1="${padding.top}" x2="${padding.left}" y2="${height - padding.bottom}" stroke="var(--line)" stroke-width="1"></line>
      <line x1="${padding.left}" y1="${padding.top}" x2="${width - padding.right}" y2="${padding.top}" stroke="var(--line)" stroke-width="1.4"></line>
      <text x="${padding.left - 8}" y="${padding.top + 4}" text-anchor="end" fill="var(--muted)" font-size="11">0%</text>
      <text x="${padding.left - 8}" y="${height - padding.bottom + 4}" text-anchor="end" fill="var(--muted)" font-size="11">${percent.format(floor * 100)}%</text>
      <polygon points="${area}" fill="var(--danger)" opacity="0.24"></polygon>
      <polyline points="${line}" fill="none" stroke="var(--danger)" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"></polyline>
    </svg>
  `;
}

function calculateDrawdowns(values) {
  let peak = 0;
  return values.map((value) => {
    peak = Math.max(peak, value);
    return peak > 0 ? (value - peak) / peak : 0;
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
      bar.style.background = value < 0 ? "var(--danger)" : "var(--success)";
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

function renderRiskMetrics() {
  const list = document.getElementById("riskMetricsList");
  if (!list) return;
  const leverage = estimateLeverageRatio(snapshot.positions);
  const largestWeight = Math.max(...snapshot.positions.map((position) => position.current_percent), 0);
  const concentration = snapshot.positions
    .slice()
    .sort((a, b) => b.current_percent - a.current_percent)
    .slice(0, 3)
    .reduce((total, position) => total + position.current_percent, 0);

  list.innerHTML = [
    ["Leverage ratio", `${percent.format(leverage)}x`],
    ["Largest position", `${percent.format(largestWeight * 100)}%`],
    ["Top 3 concentration", `${percent.format(concentration * 100)}%`],
    ["Benchmark", activeBenchmark === "portfolio" ? "Off" : activeBenchmark]
  ].map(([label, value]) => `
    <div class="risk-metric">
      <span>${label}</span>
      <strong>${value}</strong>
    </div>
  `).join("");
}

function estimateLeverageRatio(positions) {
  const leverageByTicker = {
    QLD: 2,
    TQQQ: 3
  };
  return positions.reduce((total, position) => {
    const multiple = leverageByTicker[position.ticker] || 1;
    return total + position.current_percent * multiple;
  }, 0);
}

function targetAlignment(positions) {
  const totalDrift = positions.reduce((total, position) => {
    return total + Math.abs(position.drift_percent);
  }, 0);
  return Math.max(0, Math.min(1, 1 - totalDrift / 2));
}

function applyFilter() {
  filteredPositions = getFilteredPositions();
  renderAllocation();
  renderPositions();
  renderDrift();
}

function getFilteredPositions() {
  const query = document.getElementById("tickerSearch")?.value.trim().toLowerCase() || "";
  return snapshot.positions.filter((position) => {
    return (
      position.ticker.toLowerCase().includes(query) ||
      position.name.toLowerCase().includes(query)
    );
  });
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
  filteredPositions = getFilteredPositions();
  updateCurrencyButtons();
  updateThemeButtons();
  renderSummary();
  renderWarnings();
  renderAllocation();
  renderPositions();
  renderDrift();
  renderTopCards();
  renderHistory();
  renderHealth();
  renderRiskMetrics();
}

function updateCurrencyButtons() {
  const usdButton = document.getElementById("usdButton");
  const myrButton = document.getElementById("myrButton");
  const currencyPill = document.querySelector(".currency-pill");
  if (!usdButton || !myrButton) return;

  const hasMyrRate = Boolean(snapshot.fx?.USD_MYR);
  if (!hasMyrRate && displayCurrency === "MYR") {
    displayCurrency = "USD";
  }
  usdButton.classList.toggle("active", displayCurrency === "USD");
  myrButton.classList.toggle("active", displayCurrency === "MYR");
  if (currencyPill) {
    currencyPill.dataset.active = displayCurrency === "MYR" ? "right" : "left";
  }
  usdButton.setAttribute("aria-pressed", String(displayCurrency === "USD"));
  myrButton.setAttribute("aria-pressed", String(displayCurrency === "MYR"));
  myrButton.disabled = !hasMyrRate;
}

async function init() {
  [snapshot, historyData, health] = await Promise.all([
    loadJsonWithFallback("data/latest.json", "data/latest.example.json"),
    loadJsonWithFallback("data/history.json", "data/history.example.json"),
    loadJsonWithFallback("data/health.json", "data/health.example.json")
  ]);

  document.body.dataset.theme = theme;
  document.getElementById("lightButton").addEventListener("click", () => {
    theme = "light";
    localStorage.setItem("investment-monitor-theme", theme);
    document.body.dataset.theme = theme;
    updateThemeButtons();
  });
  document.getElementById("darkButton").addEventListener("click", () => {
    theme = "dark";
    localStorage.setItem("investment-monitor-theme", theme);
    document.body.dataset.theme = theme;
    updateThemeButtons();
  });

  const usdButton = document.getElementById("usdButton");
  const myrButton = document.getElementById("myrButton");
  usdButton.addEventListener("click", () => {
    displayCurrency = "USD";
    render();
  });
  myrButton.addEventListener("click", () => {
    if (!snapshot.fx?.USD_MYR) return;
    displayCurrency = "MYR";
    render();
  });

  document.getElementById("tickerSearch").addEventListener("input", applyFilter);
  document.querySelectorAll("[data-range]").forEach((button) => {
    button.addEventListener("click", () => {
      activeRange = button.dataset.range;
      document.querySelectorAll("[data-range]").forEach((item) => {
        item.classList.toggle("active", item === button);
      });
      renderHistory();
    });
  });
  document.querySelectorAll("[data-benchmark]").forEach((button) => {
    button.addEventListener("click", () => {
      activeBenchmark = button.dataset.benchmark;
      document.querySelectorAll("[data-benchmark]").forEach((item) => {
        item.classList.toggle("active", item === button);
      });
      renderRiskMetrics();
    });
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
