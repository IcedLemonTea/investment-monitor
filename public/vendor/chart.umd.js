/*
 * Local placeholder for Chart.js UMD.
 * This example dashboard intentionally avoids CDN and external network calls.
 */
window.Chart = window.Chart || function ChartPlaceholder() {
  return {
    destroy() {}
  };
};
