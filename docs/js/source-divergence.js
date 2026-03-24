// ════════════════════════════════════════
// SOURCE DIVERGENCE
// Official vs Think Tank comparison charts
// ════════════════════════════════════════

import { THEME_LABELS } from './constants.js';
import { chartInstances } from './state.js';

const SD_COLORS = {
    official:  '#4A9E78',
    thinkTank: '#B56060',
};

const FONT = "'IBM Plex Mono', monospace";
const TOOLTIP_BASE = {
    backgroundColor: 'rgba(8,17,30,0.95)',
    borderColor: 'rgba(59,123,255,0.2)',
    borderWidth: 1,
    titleFont: { family: FONT, size: 10.5, weight: '600' },
    bodyFont: { family: FONT, size: 10 },
    padding: 10,
};

let cachedData = null;
let activeEntityTab = 'countries';

const MAX_ENTITIES = 7;

// ════════════════════════════════════════
// DATA
// ════════════════════════════════════════

async function loadDivergenceData() {
    if (cachedData) return cachedData;
    try {
        const res = await fetch('data/source_divergence.json');
        cachedData = await res.json();
        return cachedData;
    } catch (e) {
        console.error('Failed to load source_divergence.json:', e);
        return null;
    }
}

// ════════════════════════════════════════
// SHARED: build a paired horizontal bar chart
// (official green + think tank red, side by side)
// ════════════════════════════════════════

function buildPairedBarChart(ctx, labels, officialValues, thinkTankValues, tooltipCb) {
    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [
                {
                    label: 'Official',
                    data: officialValues,
                    backgroundColor: SD_COLORS.official,
                    borderColor: 'rgba(6,12,22,0.4)',
                    borderWidth: 0.5,
                    borderRadius: 2,
                    barPercentage: 0.7,
                    categoryPercentage: 0.75,
                },
                {
                    label: 'Think Tank',
                    data: thinkTankValues,
                    backgroundColor: SD_COLORS.thinkTank,
                    borderColor: 'rgba(6,12,22,0.4)',
                    borderWidth: 0.5,
                    borderRadius: 2,
                    barPercentage: 0.7,
                    categoryPercentage: 0.75,
                },
            ],
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'nearest', axis: 'y', intersect: false },
            plugins: {
                legend: { display: false },
                tooltip: {
                    ...TOOLTIP_BASE,
                    callbacks: tooltipCb,
                },
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        font: { family: FONT, size: 9 },
                        color: '#3E5570',
                        callback: v => v + '%',
                    },
                    grid: { color: 'rgba(24,42,66,.2)', lineWidth: 0.5 },
                    border: { display: false },
                },
                y: {
                    ticks: {
                        font: { family: FONT, size: 9 },
                        color: '#7A9DC0',
                    },
                    grid: { display: false },
                    border: { color: 'rgba(24,42,66,.4)' },
                },
            },
        },
    });
}

// ════════════════════════════════════════
// THEME COMPARISON
// ════════════════════════════════════════

function renderThemeComparison(data) {
    const ctx = document.getElementById('chart-sd-themes');
    if (!ctx) return;
    if (chartInstances.sdThemes) chartInstances.sdThemes.destroy();

    const gaps = data.divergence.theme_gaps;

    // Sort by max share for readable layout
    const sorted = [...gaps].sort((a, b) => {
        const maxA = Math.max(a.official_share, a.think_tank_share);
        const maxB = Math.max(b.official_share, b.think_tank_share);
        return maxB - maxA;
    });

    const labels = sorted.map(g => THEME_LABELS[g.theme] || g.theme);
    const officialData = sorted.map(g => g.official_share);
    const thinkTankData = sorted.map(g => g.think_tank_share);

    chartInstances.sdThemes = buildPairedBarChart(ctx, labels, officialData, thinkTankData, {
        title: items => {
            if (!items.length) return '';
            return labels[items[0].dataIndex];
        },
        afterTitle: items => {
            if (!items.length) return '';
            const g = sorted[items[0].dataIndex];
            const sign = g.gap > 0 ? '+' : '';
            return `Gap: ${sign}${g.gap}pp`;
        },
        label: item => {
            const val = item.parsed.x;
            return ` ${item.dataset.label}:  ${val}%`;
        },
    });
}

// ════════════════════════════════════════
// ENTITY COMPARISON — same paired bar approach
// ════════════════════════════════════════

function renderEntityComparison(data, category) {
    const ctx = document.getElementById('chart-sd-entities');
    if (!ctx) return;
    if (chartInstances.sdEntities) chartInstances.sdEntities.destroy();

    // Get top entities from both groups, merged by name
    const offEntities = data.official.top_entities[category] || [];
    const ttEntities = data.think_tank.top_entities[category] || [];

    // Build lookup maps
    const offMap = {};
    offEntities.forEach(e => { offMap[e.name] = e.share; });
    const ttMap = {};
    ttEntities.forEach(e => { ttMap[e.name] = e.share; });

    // Merge all names, sort by combined share, take top N
    const allNames = new Set([...offEntities.map(e => e.name), ...ttEntities.map(e => e.name)]);
    const merged = Array.from(allNames).map(name => ({
        name,
        official: offMap[name] || 0,
        thinkTank: ttMap[name] || 0,
        combined: (offMap[name] || 0) + (ttMap[name] || 0),
    }));
    merged.sort((a, b) => b.combined - a.combined);
    const top = merged.slice(0, MAX_ENTITIES);

    const labels = top.map(e => e.name);
    const officialData = top.map(e => e.official);
    const thinkTankData = top.map(e => e.thinkTank);

    chartInstances.sdEntities = buildPairedBarChart(ctx, labels, officialData, thinkTankData, {
        title: items => {
            if (!items.length) return '';
            return top[items[0].dataIndex].name;
        },
        afterTitle: items => {
            if (!items.length) return '';
            const e = top[items[0].dataIndex];
            const gap = +(e.thinkTank - e.official).toFixed(1);
            const sign = gap > 0 ? '+' : '';
            const dir = gap > 0 ? 'Think Tank emphasis' : gap < 0 ? 'Official emphasis' : 'Equal';
            return `Gap: ${sign}${gap}pp · ${dir}`;
        },
        label: item => {
            const val = item.parsed.x;
            return ` ${item.dataset.label}:  ${val}%`;
        },
    });
}

// ════════════════════════════════════════
// BADGES
// ════════════════════════════════════════

function updateBadges(data) {
    const offBadge = document.getElementById('sd-badge-official');
    const ttBadge = document.getElementById('sd-badge-thinktank');
    if (offBadge) offBadge.textContent = `Official · ${data.official.total_documents} docs`;
    if (ttBadge) ttBadge.textContent = `Think Tank · ${data.think_tank.total_documents} docs`;
}

// ════════════════════════════════════════
// ENTITY TAB SWITCHING
// ════════════════════════════════════════

export function initDivergenceTabs() {
    const wrap = document.getElementById('sd-entity-tabs');
    if (!wrap) return;
    wrap.querySelectorAll('.sd-entity-tab').forEach(btn => {
        btn.addEventListener('click', async () => {
            wrap.querySelectorAll('.sd-entity-tab').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            activeEntityTab = btn.dataset.category;
            const data = await loadDivergenceData();
            if (data) renderEntityComparison(data, activeEntityTab);
        });
    });
}

// ════════════════════════════════════════
// MAIN RENDER
// ════════════════════════════════════════

export async function renderSourceDivergence() {
    const data = await loadDivergenceData();
    if (!data) return;

    updateBadges(data);
    renderThemeComparison(data);
    renderEntityComparison(data, activeEntityTab);
}
