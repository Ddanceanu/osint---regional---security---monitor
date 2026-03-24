// ════════════════════════════════════════
// OVERVIEW PAGE
// Summary strip + corpus charts
// ════════════════════════════════════════

import { THEME_LABELS, CHART_COLORS } from './constants.js';
import { chartInstances } from './state.js';

// ════════════════════════════════════════
// CHART DEFAULTS
// ════════════════════════════════════════

function configureChartDefaults() {
    Chart.defaults.color = '#7A9DC0';
    Chart.defaults.borderColor = 'rgba(24,42,66,.4)';
    Chart.defaults.font.family = "'IBM Plex Sans', sans-serif";
    Chart.defaults.font.size = 12;
    Chart.defaults.plugins.legend.labels.boxWidth = 12;
    Chart.defaults.plugins.legend.labels.padding = 14;
    Chart.defaults.plugins.tooltip.backgroundColor = '#0D1828';
    Chart.defaults.plugins.tooltip.borderColor = '#223D60';
    Chart.defaults.plugins.tooltip.borderWidth = 1;
    Chart.defaults.plugins.tooltip.titleFont = { family: "'IBM Plex Mono', monospace", size: 11 };
    Chart.defaults.plugins.tooltip.bodyFont = { family: "'IBM Plex Sans', sans-serif", size: 12 };
    Chart.defaults.plugins.tooltip.padding = 10;
    Chart.defaults.plugins.tooltip.cornerRadius = 8;
}

// ════════════════════════════════════════
// RENDER OVERVIEW (orchestrator)
// ════════════════════════════════════════

export function renderOverview(docs) {
    if (!docs || !docs.length) return;
    configureChartDefaults();
    renderSummaryStrip(docs);
    renderTimelineChart(docs);
    renderSourceChart(docs);
    renderThemeChart(docs);
    renderCountryChart(docs);
    renderOrgChart(docs);
}

// ── Summary strip ──
function renderSummaryStrip(docs) {
    const el = document.getElementById('ov-summary-strip');
    if (!el) return;

    const dates = docs.map(d => d.publication_date_iso).filter(Boolean).sort();
    const firstDate = dates[0];
    const lastDate = dates[dates.length - 1];
    const daySpan = Math.max(1, Math.round((new Date(lastDate) - new Date(firstDate)) / 86400000));
    const weekSpan = Math.max(1, Math.round(daySpan / 7));
    const avgPerWeek = (docs.length / weekSpan).toFixed(1);

    const sources = [...new Set(docs.map(d => d.source_name))];
    const themes = [...new Set(docs.map(d => d.main_theme).filter(Boolean))];
    const countries = [...new Set(docs.flatMap(d => d.entities?.countries || []))];
    const orgs = [...new Set(docs.flatMap(d => d.entities?.organizations || []))];
    const persons = [...new Set(docs.flatMap(d => d.entities?.persons || []))];

    const officialCount = docs.filter(d => d.source_type === 'official').length;
    const officialPct = Math.round((officialCount / docs.length) * 100);

    const stats = [
        { label: 'Monitoring Period', value: `${daySpan} days`, detail: `${firstDate} → ${lastDate}` },
        { label: 'Collection Rate', value: `${avgPerWeek} / week`, detail: `${docs.length} documents over ${weekSpan} weeks` },
        { label: 'Source Balance', value: `${sources.length} sources`, detail: `${officialPct}% official institutional` },
        { label: 'Thematic Scope', value: `${themes.length} themes`, detail: `${countries.length} countries · ${orgs.length} orgs · ${persons.length} persons` },
    ];

    el.innerHTML = stats.map(s => `
        <div class="ov-stat-card">
            <div class="ov-stat-label">${s.label}</div>
            <div class="ov-stat-value">${s.value}</div>
            <div class="ov-stat-detail">${s.detail}</div>
        </div>
    `).join('');
}

// ── Timeline chart ──
function renderTimelineChart(docs) {
    const ctx = document.getElementById('chart-timeline');
    if (!ctx) return;
    if (chartInstances.timeline) chartInstances.timeline.destroy();

    const dates = docs.map(d => d.publication_date_iso).filter(Boolean).sort();
    if (!dates.length) return;

    const weekMap = {};
    docs.forEach(d => {
        if (!d.publication_date_iso) return;
        const dt = new Date(d.publication_date_iso);
        const day = dt.getDay();
        const diff = dt.getDate() - day + (day === 0 ? -6 : 1);
        const weekStart = new Date(dt.setDate(diff));
        const key = weekStart.toISOString().slice(0, 10);
        weekMap[key] = (weekMap[key] || 0) + 1;
    });

    const sortedWeeks = Object.keys(weekMap).sort();
    const allWeeks = [];
    const allCounts = [];
    let current = new Date(sortedWeeks[0]);
    const end = new Date(sortedWeeks[sortedWeeks.length - 1]);
    while (current <= end) {
        const key = current.toISOString().slice(0, 10);
        allWeeks.push(key);
        allCounts.push(weekMap[key] || 0);
        current.setDate(current.getDate() + 7);
    }

    chartInstances.timeline = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: allWeeks.map(w => {
                const d = new Date(w);
                return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' });
            }),
            datasets: [{
                label: 'Documents',
                data: allCounts,
                backgroundColor: 'rgba(59,123,255,.35)',
                borderColor: 'rgba(59,123,255,.8)',
                borderWidth: 1,
                borderRadius: 4,
                hoverBackgroundColor: 'rgba(59,123,255,.6)',
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { font: { family: "'IBM Plex Mono', monospace", size: 10 }, maxRotation: 45 },
                },
                y: {
                    beginAtZero: true,
                    ticks: { stepSize: 1, font: { family: "'IBM Plex Mono', monospace", size: 10 } },
                    grid: { color: 'rgba(24,42,66,.3)' },
                }
            }
        }
    });
    ctx.parentElement.style.height = '220px';
}

// ── Source distribution (doughnut) ──
function renderSourceChart(docs) {
    const ctx = document.getElementById('chart-sources');
    if (!ctx) return;
    if (chartInstances.sources) chartInstances.sources.destroy();

    const counts = {};
    docs.forEach(d => { counts[d.source_name] = (counts[d.source_name] || 0) + 1; });
    const labels = Object.keys(counts).sort((a, b) => counts[b] - counts[a]);
    const data = labels.map(l => counts[l]);

    const palette = ['#3B7BFF', '#00CFFF', '#A78BFA', '#34D399', '#FFB87A', '#FF9494', '#7A9DC0'];

    chartInstances.sources = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{
                data,
                backgroundColor: palette.slice(0, labels.length),
                borderColor: '#0D1828',
                borderWidth: 2,
                hoverOffset: 6,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '60%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { padding: 16, usePointStyle: true, pointStyle: 'circle', font: { size: 11 } }
                },
            }
        }
    });
    ctx.parentElement.style.height = '280px';
}

// ── Theme distribution (horizontal bar) ──
function renderThemeChart(docs) {
    const ctx = document.getElementById('chart-themes');
    if (!ctx) return;
    if (chartInstances.themes) chartInstances.themes.destroy();

    const counts = {};
    docs.forEach(d => {
        const key = d.main_theme || 'other_mixed';
        counts[key] = (counts[key] || 0) + 1;
    });
    const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]);
    const labels = sorted.map(([k]) => THEME_LABELS[k] || k);
    const data = sorted.map(([, v]) => v);
    const colors = sorted.map(([k]) => CHART_COLORS[k] || '#7A9DC0');

    chartInstances.themes = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                data,
                backgroundColor: colors.map(c => c + '55'),
                borderColor: colors,
                borderWidth: 1,
                borderRadius: 4,
                hoverBackgroundColor: colors.map(c => c + '99'),
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: { legend: { display: false } },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: { stepSize: 1, font: { family: "'IBM Plex Mono', monospace", size: 10 } },
                    grid: { color: 'rgba(24,42,66,.3)' },
                },
                y: {
                    grid: { display: false },
                    ticks: { font: { size: 11 } },
                }
            }
        }
    });
    ctx.parentElement.style.height = '280px';
}

// ── Country frequency (horizontal bar) ──
function renderCountryChart(docs) {
    const ctx = document.getElementById('chart-countries');
    if (!ctx) return;
    if (chartInstances.countries) chartInstances.countries.destroy();

    const counts = {};
    docs.forEach(d => {
        (d.entities?.countries || []).forEach(c => { counts[c] = (counts[c] || 0) + 1; });
    });
    const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, 12);
    const labels = sorted.map(([k]) => k);
    const data = sorted.map(([, v]) => v);

    chartInstances.countries = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                data,
                backgroundColor: 'rgba(0,207,255,.3)',
                borderColor: 'rgba(0,207,255,.7)',
                borderWidth: 1,
                borderRadius: 4,
                hoverBackgroundColor: 'rgba(0,207,255,.55)',
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: { legend: { display: false } },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: { stepSize: 1, font: { family: "'IBM Plex Mono', monospace", size: 10 } },
                    grid: { color: 'rgba(24,42,66,.3)' },
                },
                y: {
                    grid: { display: false },
                    ticks: { font: { size: 11 } },
                }
            }
        }
    });
    ctx.parentElement.style.height = '320px';
}

// ── Organization frequency (horizontal bar) ──
function renderOrgChart(docs) {
    const ctx = document.getElementById('chart-orgs');
    if (!ctx) return;
    if (chartInstances.orgs) chartInstances.orgs.destroy();

    const counts = {};
    docs.forEach(d => {
        (d.entities?.organizations || []).forEach(o => { counts[o] = (counts[o] || 0) + 1; });
    });
    const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, 10);
    const labels = sorted.map(([k]) => k);
    const data = sorted.map(([, v]) => v);

    chartInstances.orgs = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                data,
                backgroundColor: 'rgba(167,139,250,.3)',
                borderColor: 'rgba(167,139,250,.7)',
                borderWidth: 1,
                borderRadius: 4,
                hoverBackgroundColor: 'rgba(167,139,250,.55)',
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: { legend: { display: false } },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: { stepSize: 1, font: { family: "'IBM Plex Mono', monospace", size: 10 } },
                    grid: { color: 'rgba(24,42,66,.3)' },
                },
                y: {
                    grid: { display: false },
                    ticks: { font: { size: 11 } },
                }
            }
        }
    });
    ctx.parentElement.style.height = '320px';
}
