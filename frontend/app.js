(function () {
  const data = window.DASHBOARD_DATA || { records: [], options: {} };
  const state = {
    region: "all",
    city: "all",
    road: "all",
    risk: "all",
  };

  const els = {
    region: document.getElementById("regionFilter"),
    city: document.getElementById("cityFilter"),
    road: document.getElementById("roadFilter"),
    risk: document.getElementById("riskFilter"),
    scope: document.getElementById("scopeLabel"),
    total: document.getElementById("kpiTotal"),
    riskKpi: document.getElementById("kpiRisk"),
    deaths: document.getElementById("kpiDeaths"),
    injured: document.getElementById("kpiInjured"),
    monthInsight: document.getElementById("monthInsight"),
    cityBars: document.getElementById("cityBars"),
    causeBars: document.getElementById("causeBars"),
    roadBars: document.getElementById("roadBars"),
    hotspots: document.getElementById("hotspotsTable"),
    monthChart: document.getElementById("monthChart"),
    hourChart: document.getElementById("hourChart"),
  };

  function init() {
    fillSelect(els.city, data.options.municipios || []);
    fillSelect(els.road, data.options.rodovias || []);
    fillSelect(els.risk, data.options.riscos || []);

    [els.region, els.city, els.road, els.risk].forEach((select) => {
      select.addEventListener("change", () => {
        state.region = els.region.value;
        state.city = els.city.value;
        state.road = els.road.value;
        state.risk = els.risk.value;
        render();
      });
    });

    render();
  }

  function fillSelect(select, values) {
    values.forEach((value) => {
      const option = document.createElement("option");
      option.value = value;
      option.textContent = value;
      select.appendChild(option);
    });
  }

  function filteredRecords() {
    return data.records.filter((row) => {
      if (state.region === "gv" && !row.regiao_grande_vitoria) return false;
      if (state.city !== "all" && row.municipio !== state.city) return false;
      if (state.road !== "all" && row.rodovia_label !== state.road) return false;
      if (state.risk !== "all" && row.nivel_risco !== state.risk) return false;
      return true;
    });
  }

  function render() {
    const rows = filteredRecords();
    els.scope.textContent = state.region === "gv" ? "Grande Vitória" : "ES";
    renderKpis(rows);
    renderMonthChart(rows);
    renderHourChart(rows);
    renderBars(els.cityBars, groupCount(rows, "municipio"), 8);
    renderBars(els.causeBars, groupCount(rows, "causa"), 8);
    renderBars(els.roadBars, groupCount(rows, "rodovia_label"), 8);
    renderHotspots(rows);
  }

  function renderKpis(rows) {
    els.total.textContent = formatNumber(rows.length);
    els.riskKpi.textContent = formatNumber(sum(rows, "risco_alto"));
    els.deaths.textContent = formatNumber(sum(rows, "mortos"));
    els.injured.textContent = formatNumber(sum(rows, "feridos"));
  }

  function renderMonthChart(rows) {
    const values = Array.from({ length: 12 }, (_, index) => ({
      label: String(index + 1).padStart(2, "0"),
      value: 0,
    }));
    rows.forEach((row) => {
      const month = Number(row.mes);
      if (month >= 1 && month <= 12) values[month - 1].value += 1;
    });

    const top = values.reduce((best, item) => (item.value > best.value ? item : best), values[0]);
    els.monthInsight.textContent = top ? `Pico: mês ${top.label}` : "";
    drawBarChart(els.monthChart, values, "#0f766e");
  }

  function renderHourChart(rows) {
    const values = Array.from({ length: 24 }, (_, index) => ({
      label: `${String(index).padStart(2, "0")}h`,
      value: 0,
    }));
    rows.forEach((row) => {
      const hour = Number(row.hora_dia);
      if (hour >= 0 && hour <= 23) values[hour].value += 1;
    });
    drawBarChart(els.hourChart, values, "#c2410c");
  }

  function renderBars(container, items, limit) {
    container.innerHTML = "";
    const top = items.slice(0, limit);
    const max = Math.max(1, ...top.map((item) => item.value));

    top.forEach((item) => {
      const row = document.createElement("div");
      row.className = "bar-row";
      row.innerHTML = `
        <div class="bar-meta">
          <span title="${escapeHtml(item.label)}">${escapeHtml(item.label)}</span>
          <span>${formatNumber(item.value)}</span>
        </div>
        <div class="bar-track">
          <div class="bar-fill" style="width: ${(item.value / max) * 100}%"></div>
        </div>
      `;
      container.appendChild(row);
    });
  }

  function renderHotspots(rows) {
    const map = new Map();
    rows.forEach((row) => {
      const km = Number(row.km);
      const key = `${row.rodovia_label || "N/I"}|${Number.isFinite(km) ? km.toFixed(1) : "N/I"}|${row.municipio || "N/I"}`;
      if (!map.has(key)) {
        map.set(key, {
          road: row.rodovia_label || "N/I",
          km: Number.isFinite(km) ? km.toFixed(1) : "N/I",
          city: row.municipio || "N/I",
          total: 0,
          highRisk: 0,
        });
      }
      const item = map.get(key);
      item.total += 1;
      item.highRisk += Number(row.risco_alto || 0);
    });

    const top = Array.from(map.values())
      .sort((a, b) => b.total - a.total || b.highRisk - a.highRisk)
      .slice(0, 25);

    els.hotspots.innerHTML = top
      .map(
        (item) => `
          <tr>
            <td>${escapeHtml(item.road)}</td>
            <td>${escapeHtml(item.km)}</td>
            <td>${escapeHtml(item.city)}</td>
            <td>${formatNumber(item.total)}</td>
            <td>${formatNumber(item.highRisk)}</td>
          </tr>
        `
      )
      .join("");
  }

  function groupCount(rows, key) {
    const counts = new Map();
    rows.forEach((row) => {
      const label = row[key] || "N/I";
      counts.set(label, (counts.get(label) || 0) + 1);
    });
    return Array.from(counts, ([label, value]) => ({ label, value })).sort((a, b) => b.value - a.value);
  }

  function drawBarChart(canvas, values, color) {
    const context = canvas.getContext("2d");
    const ratio = window.devicePixelRatio || 1;
    const width = canvas.clientWidth;
    const height = Number(canvas.getAttribute("height"));
    canvas.width = width * ratio;
    canvas.height = height * ratio;
    context.scale(ratio, ratio);
    context.clearRect(0, 0, width, height);

    const padding = { top: 16, right: 14, bottom: 32, left: 44 };
    const chartWidth = width - padding.left - padding.right;
    const chartHeight = height - padding.top - padding.bottom;
    const max = Math.max(1, ...values.map((item) => item.value));
    const gap = 5;
    const barWidth = Math.max(4, chartWidth / values.length - gap);

    context.strokeStyle = "#d8d0c3";
    context.beginPath();
    context.moveTo(padding.left, padding.top);
    context.lineTo(padding.left, padding.top + chartHeight);
    context.lineTo(width - padding.right, padding.top + chartHeight);
    context.stroke();

    context.fillStyle = color;
    values.forEach((item, index) => {
      const x = padding.left + index * (barWidth + gap);
      const barHeight = (item.value / max) * chartHeight;
      const y = padding.top + chartHeight - barHeight;
      context.fillRect(x, y, barWidth, barHeight);
    });

    context.fillStyle = "#68726b";
    context.font = "12px Arial";
    values.forEach((item, index) => {
      if (values.length > 12 && index % 2 !== 0) return;
      const x = padding.left + index * (barWidth + gap);
      context.fillText(item.label, x, height - 10);
    });

    context.fillText(formatNumber(max), 6, padding.top + 8);
    context.fillText("0", 24, padding.top + chartHeight);
  }

  function sum(rows, key) {
    return rows.reduce((total, row) => total + Number(row[key] || 0), 0);
  }

  function formatNumber(value) {
    return new Intl.NumberFormat("pt-BR", { maximumFractionDigits: 0 }).format(value || 0);
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  window.addEventListener("resize", render);
  init();
})();