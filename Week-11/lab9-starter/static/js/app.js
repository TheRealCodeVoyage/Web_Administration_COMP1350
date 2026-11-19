// Lab 9 starter script.
// Part 2: change ASSET_VERSION, push to GitHub, and watch the new value go live
// through your CloudFront distribution.
const ASSET_VERSION = "v1";

function ms(value) {
  return Math.round(value) + " ms";
}

function size(entry) {
  if (entry.transferSize > 0) return (entry.transferSize / 1024).toFixed(0) + " KB";
  if (entry.decodedBodySize > 0) return "browser cache";
  return "hidden";
}

function cell(row, text, className) {
  const td = document.createElement("td");
  td.textContent = text;
  if (className) td.className = className;
  row.appendChild(td);
}

function report() {
  document.getElementById("asset-version").textContent = ASSET_VERSION;

  const nav = performance.getEntriesByType("navigation")[0];
  document.getElementById("page-load").textContent = nav ? ms(nav.loadEventEnd) : "n/a";
  document.getElementById("html-host").textContent = location.host;

  const files = performance
    .getEntriesByType("resource")
    .filter((e) => ["link", "script", "img", "css"].includes(e.initiatorType));

  const tbody = document.getElementById("resources");
  tbody.replaceChildren();
  const rows = [];

  for (const entry of files) {
    const url = new URL(entry.name);
    const from = url.host === location.host ? "this server (" + url.host + ")" : url.host;
    const row = document.createElement("tr");
    cell(row, url.pathname.split("/").pop());
    cell(row, from);
    cell(row, ms(entry.duration), "num");
    cell(row, size(entry), "num");
    tbody.appendChild(row);
    rows.push({ file: url.pathname, from, ms: Math.round(entry.duration), size: size(entry) });
  }

  console.table(rows);
}

// loadEventEnd is only recorded after every load handler has finished,
// so wait one tick before reading it.
window.addEventListener("load", () => setTimeout(report, 0));
