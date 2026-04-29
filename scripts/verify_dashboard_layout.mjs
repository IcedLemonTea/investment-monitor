import { mkdtemp, rm, readFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { spawn } from "node:child_process";

const DEFAULT_URL = "http://127.0.0.1:8765/";
const DEFAULT_VIEWPORT = { width: 1440, height: 1000 };

const args = parseArgs(process.argv.slice(2));
const url = args.url || DEFAULT_URL;
const viewport = {
  width: Number(args.width || DEFAULT_VIEWPORT.width),
  height: Number(args.height || DEFAULT_VIEWPORT.height),
};

let browserProcess;
let profileDir;

try {
  const browser = args.browser || findBrowser();
  profileDir = await mkdtemp(join(tmpdir(), "dashboard-layout-cdp-"));
  browserProcess = launchBrowser(browser, profileDir);
  const port = await readDevToolsPort(profileDir);
  const wsUrl = await getPageWebSocketUrl(port);
  const cdp = await connectCdp(wsUrl);

  await cdp.send("Page.enable");
  await cdp.send("Runtime.enable");
  await cdp.send("Emulation.setDeviceMetricsOverride", {
    width: viewport.width,
    height: viewport.height,
    deviceScaleFactor: 1,
    mobile: false,
  });

  const load = cdp.waitFor("Page.loadEventFired", 15000);
  await cdp.send("Page.navigate", { url });
  await load;
  await waitForDashboard(cdp);

  const result = await cdp.send("Runtime.evaluate", {
    expression: `(${layoutAssertions.toString()})(${JSON.stringify({ viewport })})`,
    awaitPromise: true,
    returnByValue: true,
  });

  if (result.exceptionDetails) {
    throw new Error(formatException(result.exceptionDetails));
  }

  const failures = result.result?.value || [];
  if (failures.length > 0) {
    console.error("Dashboard layout validation failed:");
    failures.forEach((failure, index) => {
      console.error(`${index + 1}. ${failure}`);
    });
    process.exitCode = 1;
  } else {
    console.log(`dashboard layout ok: ${url} (${viewport.width}x${viewport.height})`);
  }

  cdp.close();
} finally {
  if (browserProcess && !browserProcess.killed) {
    browserProcess.kill();
    await waitForProcessExit(browserProcess, 3000);
  }
  if (profileDir) {
    await rm(profileDir, { recursive: true, force: true, maxRetries: 5, retryDelay: 150 });
  }
}

function parseArgs(rawArgs) {
  const parsed = {};
  for (let index = 0; index < rawArgs.length; index += 1) {
    const arg = rawArgs[index];
    if (!arg.startsWith("--")) continue;
    const key = arg.slice(2);
    const next = rawArgs[index + 1];
    if (next && !next.startsWith("--")) {
      parsed[key] = next;
      index += 1;
    } else {
      parsed[key] = true;
    }
  }
  return parsed;
}

function findBrowser() {
  const candidates = [
    "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    "C:/Program Files/Microsoft/Edge/Application/msedge.exe",
    "C:/Program Files/Google/Chrome/Application/chrome.exe",
    "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe",
  ];
  const browser = candidates.find((candidate) => existsSync(candidate));
  if (!browser) {
    throw new Error("No supported Edge or Chrome executable found.");
  }
  return browser;
}

function launchBrowser(browser, userDataDir) {
  return spawn(browser, [
    "--headless=new",
    "--disable-gpu",
    "--disable-background-networking",
    "--disable-default-apps",
    "--disable-extensions",
    "--no-first-run",
    "--remote-debugging-port=0",
    `--user-data-dir=${userDataDir}`,
    "about:blank",
  ], {
    stdio: "ignore",
    windowsHide: true,
  });
}

async function readDevToolsPort(userDataDir) {
  const activePortPath = join(userDataDir, "DevToolsActivePort");
  const started = Date.now();
  while (Date.now() - started < 10000) {
    if (existsSync(activePortPath)) {
      const [port] = (await readFile(activePortPath, "utf8")).trim().split(/\r?\n/);
      if (port) return Number(port);
    }
    await delay(100);
  }
  throw new Error("Timed out waiting for Chromium DevToolsActivePort.");
}

async function getPageWebSocketUrl(port) {
  const response = await fetch(`http://127.0.0.1:${port}/json/list`);
  if (!response.ok) {
    throw new Error(`Unable to list CDP targets: HTTP ${response.status}`);
  }
  const targets = await response.json();
  const page = targets.find((target) => target.type === "page" && target.webSocketDebuggerUrl);
  if (!page) {
    throw new Error("No CDP page target found.");
  }
  return page.webSocketDebuggerUrl;
}

function connectCdp(wsUrl) {
  const ws = new WebSocket(wsUrl);
  let nextId = 1;
  const pending = new Map();
  const eventWaiters = new Map();

  ws.addEventListener("message", (event) => {
    const message = JSON.parse(event.data);
    if (message.id) {
      const request = pending.get(message.id);
      if (!request) return;
      pending.delete(message.id);
      if (message.error) {
        request.reject(new Error(`${message.error.message}: ${message.error.data || ""}`.trim()));
      } else {
        request.resolve(message.result || {});
      }
      return;
    }

    const waiters = eventWaiters.get(message.method) || [];
    eventWaiters.set(message.method, waiters.filter((waiter) => {
      waiter.resolve(message.params || {});
      clearTimeout(waiter.timeout);
      return false;
    }));
  });

  return new Promise((resolve, reject) => {
    ws.addEventListener("open", () => {
      resolve({
        send(method, params = {}) {
          const id = nextId;
          nextId += 1;
          ws.send(JSON.stringify({ id, method, params }));
          return new Promise((requestResolve, requestReject) => {
            pending.set(id, { resolve: requestResolve, reject: requestReject });
          });
        },
        waitFor(method, timeoutMs) {
          return new Promise((waiterResolve, waiterReject) => {
            const timeout = setTimeout(() => {
              const waiters = eventWaiters.get(method) || [];
              eventWaiters.set(method, waiters.filter((waiter) => waiter.resolve !== waiterResolve));
              waiterReject(new Error(`Timed out waiting for CDP event ${method}.`));
            }, timeoutMs);
            const waiters = eventWaiters.get(method) || [];
            waiters.push({ resolve: waiterResolve, timeout });
            eventWaiters.set(method, waiters);
          });
        },
        close() {
          ws.close();
        },
      });
    }, { once: true });
    ws.addEventListener("error", () => reject(new Error("Failed to connect to CDP WebSocket.")), { once: true });
  });
}

async function waitForDashboard(cdp) {
  const started = Date.now();
  while (Date.now() - started < 15000) {
    const result = await cdp.send("Runtime.evaluate", {
      expression: `Boolean(
        document.readyState === "complete" &&
        document.querySelector("#allocationBars > *") &&
        document.querySelector("#portfolioValueChart svg") &&
        document.querySelector("#dailyPnlChart svg") &&
        document.querySelector("#drawdownChart svg") &&
        document.querySelector("#topPositionsList .heatmap-tile")
      )`,
      returnByValue: true,
    });
    if (result.result?.value === true) return;
    await delay(150);
  }
  throw new Error("Timed out waiting for dashboard charts and heatmap to render.");
}

function formatException(exceptionDetails) {
  return exceptionDetails.exception?.description ||
    exceptionDetails.text ||
    "Runtime.evaluate failed inside dashboard layout assertions.";
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function waitForProcessExit(process, timeoutMs) {
  if (process.exitCode !== null || process.signalCode !== null) {
    return Promise.resolve();
  }
  return new Promise((resolve) => {
    const timeout = setTimeout(resolve, timeoutMs);
    process.once("exit", () => {
      clearTimeout(timeout);
      resolve();
    });
  });
}

function layoutAssertions({ viewport }) {
  const failures = [];
  const pxTolerance = 1.5;

  const bySelector = (selector) => {
    const element = document.querySelector(selector);
    if (!element) failures.push(`Missing required element: ${selector}`);
    return element;
  };
  const rectOf = (element) => element.getBoundingClientRect();
  const css = (element) => getComputedStyle(element);
  const approx = (actual, expected, tolerance = pxTolerance) => Math.abs(actual - expected) <= tolerance;
  const number = (value) => Number.parseFloat(value) || 0;

  const summaryGrid = bySelector(".summary-grid");
  const allocation = bySelector("#allocation");
  const performance = bySelector("#performance");
  if (summaryGrid && allocation && performance) {
    const summaryToAllocation = rectOf(allocation).top - rectOf(summaryGrid).bottom;
    const allocationToPerformance = rectOf(performance).top - rectOf(allocation).bottom;
    if (!approx(summaryToAllocation, 24)) {
      failures.push(`Expected 24px vertical gap between .summary-grid and #allocation, got ${summaryToAllocation.toFixed(2)}px.`);
    }
    if (!approx(allocationToPerformance, 24)) {
      failures.push(`Expected 24px vertical gap between #allocation and #performance, got ${allocationToPerformance.toFixed(2)}px.`);
    }
    const leftDelta = Math.abs(rectOf(allocation).left - rectOf(performance).left);
    if (leftDelta > pxTolerance) {
      failures.push(`#allocation and #performance left edges differ by ${leftDelta.toFixed(2)}px.`);
    }
  }

  const sidebar = bySelector(".sidebar");
  const sidebarBottom = bySelector(".sidebar-bottom");
  if (sidebar) {
    const sidebarRect = rectOf(sidebar);
    const sidebarPosition = css(sidebar).position;
    if (!["fixed", "sticky"].includes(sidebarPosition)) {
      failures.push(`Expected .sidebar to be fixed or sticky, got position: ${sidebarPosition}.`);
    }
    if (!approx(sidebarRect.top, 0)) {
      failures.push(`Expected .sidebar top to be 0px, got ${sidebarRect.top.toFixed(2)}px.`);
    }
    if (!approx(sidebarRect.height, window.innerHeight)) {
      failures.push(`Expected .sidebar height to equal 100vh (${window.innerHeight}px), got ${sidebarRect.height.toFixed(2)}px.`);
    }
  }
  if (sidebarBottom) {
    const bottomGap = window.innerHeight - rectOf(sidebarBottom).bottom;
    if (bottomGap < 24 - pxTolerance) {
      failures.push(`Expected .sidebar-bottom at least 24px above viewport bottom, got ${bottomGap.toFixed(2)}px.`);
    }
  }

  document.querySelectorAll(".metric").forEach((metric, index) => {
    const style = css(metric);
    const paddings = [
      ["top", number(style.paddingTop)],
      ["right", number(style.paddingRight)],
      ["bottom", number(style.paddingBottom)],
      ["left", number(style.paddingLeft)],
    ];
    paddings.forEach(([side, value]) => {
      if (!approx(value, 24)) {
        failures.push(`Expected KPI ${index + 1} ${side} padding to be 24px, got ${value.toFixed(2)}px.`);
      }
    });

    const value = metric.querySelector("strong");
    if (value && value.scrollWidth > value.clientWidth + pxTolerance) {
      failures.push(`KPI ${index + 1} value overflows horizontally: scrollWidth ${value.scrollWidth}px, clientWidth ${value.clientWidth}px.`);
    }
    if (value && rectOf(value).right > rectOf(metric).right - number(style.paddingRight) + pxTolerance) {
      failures.push(`KPI ${index + 1} value extends beyond the padded content box.`);
    }
  });

  const portfolioChart = bySelector("#portfolioValueChart");
  const dailyPnlChart = bySelector("#dailyPnlChart");
  if (portfolioChart && dailyPnlChart) {
    const bottomDelta = Math.abs(rectOf(portfolioChart).bottom - rectOf(dailyPnlChart).bottom);
    if (bottomDelta > pxTolerance) {
      failures.push(`#portfolioValueChart and #dailyPnlChart bottoms differ by ${bottomDelta.toFixed(2)}px.`);
    }
  }

  const rangeToggle = bySelector(".range-toggle");
  const portfolioHeader = document.querySelector("#portfolioValueChart")?.closest(".chart-block")?.querySelector(".mini-chart-heading");
  if (rangeToggle && portfolioHeader) {
    const toggleRect = rectOf(rangeToggle);
    const headerRect = rectOf(portfolioHeader);
    if (!portfolioHeader.contains(rangeToggle)) {
      failures.push("Expected .range-toggle to be inside the portfolio chart header.");
    }
    if (toggleRect.top < headerRect.top - pxTolerance || toggleRect.bottom > headerRect.bottom + pxTolerance) {
      failures.push("Expected .range-toggle to be vertically contained within the portfolio chart header.");
    }
    if (Math.abs(toggleRect.right - headerRect.right) > 8) {
      failures.push(`Expected .range-toggle to be anchored to the portfolio chart header right edge, got ${Math.abs(toggleRect.right - headerRect.right).toFixed(2)}px offset.`);
    }
  }

  document.querySelectorAll("#performance table").forEach((table, tableIndex) => {
    table.querySelectorAll("tr").forEach((row, rowIndex) => {
      [2, 3].forEach((column) => {
        const cell = row.children[column - 1];
        if (!cell) return;
        const textAlign = css(cell).textAlign;
        if (textAlign !== "right" && textAlign !== "end") {
          failures.push(`Expected table ${tableIndex + 1} row ${rowIndex + 1} column ${column} to be right aligned, got ${textAlign}.`);
        }
      });
    });
  });

  const drawdownChart = bySelector("#drawdownChart");
  if (drawdownChart) {
    const polygon = drawdownChart.querySelector("svg polygon");
    const svg = drawdownChart.querySelector("svg");
    if (!polygon) {
      failures.push("Expected #drawdownChart to contain a filled polygon.");
    } else {
      const opacity = number(polygon.getAttribute("opacity") || css(polygon).opacity);
      if (opacity > 0.2) {
        failures.push(`Expected drawdown fill opacity <= 0.2, got ${opacity}.`);
      }
    }
    if (svg) {
      const horizontalLines = [...svg.querySelectorAll("line")].filter((line) => line.getAttribute("y1") === line.getAttribute("y2"));
      const topPlotY = Math.min(...[...svg.querySelectorAll("line")].map((line) => number(line.getAttribute("y1"))));
      const zeroLine = horizontalLines.find((line) => approx(number(line.getAttribute("y1")), topPlotY, 0.1));
      if (!zeroLine) {
        failures.push("Expected drawdown 0% horizontal line to sit at the top plot y.");
      }
    }
  }

  document.querySelectorAll("#topPositionsList .heatmap-tile").forEach((tile) => {
    const tileRect = rectOf(tile);
    if (tileRect.width >= 60 && tileRect.height >= 40) return;
    const visibleLabels = [...tile.querySelectorAll("strong, span")].filter((label) => {
      const labelStyle = css(label);
      return !(labelStyle.display === "none" ||
        labelStyle.visibility === "hidden" ||
        Number.parseFloat(labelStyle.opacity) === 0 ||
        rectOf(label).width === 0 ||
        rectOf(label).height === 0);
    });
    if (visibleLabels.length > 0) {
      failures.push(`Expected heatmap text to be hidden for ${tile.title || "small tile"} (${tileRect.width.toFixed(2)}x${tileRect.height.toFixed(2)}px).`);
    }
  });

  const heatmap = bySelector("#topPositionsList");
  const qldTile = [...document.querySelectorAll("#topPositionsList .heatmap-tile")].find((tile) => {
    const title = tile.getAttribute("title") || "";
    return /^QLD\b/.test(title) || /\bQLD\b/.test(tile.textContent || "");
  });
  if (heatmap && !qldTile) {
    failures.push("Expected QLD tile in portfolio heatmap.");
  }
  if (heatmap && qldTile) {
    const heatmapRect = rectOf(heatmap);
    const qldRect = rectOf(qldTile);
    const actualShare = (qldRect.width * qldRect.height) / (heatmapRect.width * heatmapRect.height);
    const expectedShare = 0.5105;
    const tolerance = 0.035;
    if (Math.abs(actualShare - expectedShare) > tolerance) {
      failures.push(`Expected QLD treemap area near 51.05% (+/- ${(tolerance * 100).toFixed(1)}%), got ${(actualShare * 100).toFixed(2)}%.`);
    }
  }

  if (window.innerWidth !== viewport.width || window.innerHeight !== viewport.height) {
    failures.push(`Expected viewport ${viewport.width}x${viewport.height}, got ${window.innerWidth}x${window.innerHeight}.`);
  }

  return failures;
}
