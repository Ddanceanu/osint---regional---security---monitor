// ════════════════════════════════════════
// ACTOR TRAJECTORIES
// Source-normalized visibility over 90 days
// ════════════════════════════════════════

import { THEME_LABELS } from './constants.js';

// ── Colour palette for up to 8 simultaneous actors ──
const ACTOR_COLORS = [
    { line: '#00CFFF', bg: 'rgba(0,207,255,0.08)',   border: 'rgba(0,207,255,0.3)'   },
    { line: '#ff4d6a', bg: 'rgba(255,77,106,0.08)',  border: 'rgba(255,77,106,0.3)'  },
    { line: '#a78bfa', bg: 'rgba(167,139,250,0.08)', border: 'rgba(167,139,250,0.3)' },
    { line: '#f59e0b', bg: 'rgba(245,158,11,0.08)',  border: 'rgba(245,158,11,0.3)'  },
    { line: '#34d399', bg: 'rgba(52,211,153,0.08)',  border: 'rgba(52,211,153,0.3)'  },
    { line: '#fb923c', bg: 'rgba(251,146,60,0.08)',  border: 'rgba(251,146,60,0.3)'  },
    { line: '#e879f9', bg: 'rgba(232,121,249,0.08)', border: 'rgba(232,121,249,0.3)' },
    { line: '#94a3b8', bg: 'rgba(148,163,184,0.08)', border: 'rgba(148,163,184,0.3)' },
];

const MAX_ACTORS = 8;
const DISPLAY_WEEKS = 8;

// ── Module state ──
let chartInstance    = null;
let cachedData       = null;
let activeActors     = [];   // [{name, color, trajectory, currentRate}]
let colorIndex       = 0;
let usedColors       = {};   // name -> colorIndex
let activeCategory   = 'countries';

// ════════════════════════════════════════
// DATA
// ════════════════════════════════════════

async function loadData() {
    if (cachedData) return cachedData;
    try {
        const res = await fetch('data/actor_trajectories.json');
        cachedData = await res.json();
        return cachedData;
    } catch (e) {
        console.error('[AT] Failed to load actor_trajectories.json', e);
        return null;
    }
}

// ════════════════════════════════════════
// COLOUR MANAGEMENT
// ════════════════════════════════════════

function assignColor(name) {
    if (usedColors[name] != null) return ACTOR_COLORS[usedColors[name]];
    const idx = colorIndex % ACTOR_COLORS.length;
    usedColors[name] = idx;
    colorIndex++;
    return ACTOR_COLORS[idx];
}

function releaseColor(name) {
    delete usedColors[name];
}

// ════════════════════════════════════════
// DISPLAY NAME
// ════════════════════════════════════════

function displayName(name, category) {
    if (category === 'themes') return THEME_LABELS[name] || name;
    return name;
}

// ════════════════════════════════════════
// CHART
// ════════════════════════════════════════

function buildDatasets() {
    return activeActors.map(actor => {
        const color = ACTOR_COLORS[usedColors[actor.name]];
        return {
            label: actor.displayName,
            data: actor.trajectory.slice(-DISPLAY_WEEKS),
            borderColor: color.line,
            backgroundColor: (ctx) => {
                const chart = ctx.chart;
                const { ctx: c, chartArea } = chart;
                if (!chartArea) return 'transparent';
                const gradient = c.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
                gradient.addColorStop(0, color.line.replace(')', ', 0.06)').replace('rgb', 'rgba'));
                gradient.addColorStop(1, 'transparent');
                return gradient;
            },
            borderWidth: 2,
            fill: true,
            tension: 0.35,
            pointRadius: 2.5,
            pointHoverRadius: 5,
            pointBackgroundColor: color.line,
            pointBorderColor: '#0a121e',
            pointBorderWidth: 1.5,
        };
    });
}

function renderChart(data) {
    const canvas = document.getElementById('at-chart');
    if (!canvas) return;

    if (chartInstance) {
        chartInstance.destroy();
        chartInstance = null;
    }

    const wrap = canvas.parentElement;

    if (activeActors.length === 0) {
        wrap.innerHTML = '<div class="at-empty">Select actors below to visualise their trajectories</div>';
        return;
    }

    // Restore canvas if we replaced it with empty state
    if (!document.getElementById('at-chart')) {
        wrap.innerHTML = '<canvas id="at-chart"></canvas>';
    }

    const ctx = document.getElementById('at-chart').getContext('2d');
    const labels = data.week_labels.slice(-DISPLAY_WEEKS);

    chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: buildDatasets(),
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 600, easing: 'easeInOutQuart' },
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#0a121e',
                    borderColor: 'rgba(255,255,255,0.08)',
                    borderWidth: 1,
                    padding: 12,
                    titleFont: { size: 11, family: "'JetBrains Mono', monospace", weight: '600' },
                    bodyFont:  { size: 10, family: "'JetBrains Mono', monospace" },
                    titleColor: 'rgba(255,255,255,0.8)',
                    bodyColor:  'rgba(255,255,255,0.6)',
                    callbacks: {
                        title: items => `Week of ${items[0].label}`,
                        label: ctx => {
                            const color = ACTOR_COLORS[usedColors[activeActors[ctx.datasetIndex]?.name]];
                            return `  ${ctx.dataset.label}: ${ctx.parsed.y.toFixed(1)}%`;
                        },
                        labelColor: ctx => ({
                            borderColor: 'transparent',
                            backgroundColor: ACTOR_COLORS[usedColors[activeActors[ctx.datasetIndex]?.name]]?.line || '#fff',
                            borderRadius: 4,
                        }),
                    },
                },
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255,255,255,0.04)', drawBorder: false },
                    ticks: {
                        color: '#5a6577',
                        font: { size: 9, family: "'JetBrains Mono', monospace" },
                        maxRotation: 30,
                        maxTicksLimit: 12,
                    },
                },
                y: {
                    beginAtZero: true,
                    grid: { color: 'rgba(255,255,255,0.04)', drawBorder: false },
                    ticks: {
                        color: '#5a6577',
                        font: { size: 9, family: "'JetBrains Mono', monospace" },
                        callback: v => v + '%',
                    },
                },
            },
        },
    });
}

// ════════════════════════════════════════
// SELECTED BAR (chips)
// ════════════════════════════════════════

function renderSelectedBar() {
    const bar = document.getElementById('at-selected-bar');
    if (!bar) return;

    if (activeActors.length === 0) {
        bar.innerHTML = '<span style="font-size:0.7rem;color:rgba(255,255,255,0.2);font-style:italic;">No actors selected — pick from the list below</span>';
        return;
    }

    const chips = activeActors.map(actor => {
        const color = ACTOR_COLORS[usedColors[actor.name]];
        const rateStr = actor.currentRate != null ? `${actor.currentRate.toFixed(1)}%` : '';
        return `
            <div class="at-chip" data-name="${actor.name}"
                 style="background:${color.bg};border-color:${color.border};">
                <div class="at-chip-dot" style="background:${color.line}"></div>
                <span class="at-chip-name">${actor.displayName}</span>
                <span class="at-chip-rate" style="color:${color.line}">${rateStr}</span>
                <span class="at-chip-remove">✕</span>
            </div>
        `;
    }).join('');

    const warning = activeActors.length >= MAX_ACTORS
        ? `<span class="at-max-warning">Max ${MAX_ACTORS} actors</span>`
        : '';

    bar.innerHTML = chips + warning;

    bar.querySelectorAll('.at-chip').forEach(chip => {
        chip.addEventListener('click', () => removeActor(chip.dataset.name));
    });
}

// ════════════════════════════════════════
// SIDEBAR SELECTOR
// ════════════════════════════════════════

function initSidebar(data) {
    const search = document.getElementById('at-search');
    const tabs   = document.querySelectorAll('.at-cat-tab');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            activeCategory = tab.dataset.cat;
            if (search) search.value = '';
            renderDropdownList(data, '');
        });
    });

    if (search) {
        renderDropdownList(data, '');
        search.addEventListener('input', () => {
            renderDropdownList(data, search.value.trim().toLowerCase());
        });
    }
}

function renderDropdownList(data, filter) {
    const list = document.getElementById('at-dropdown-list');
    if (!list) return;

    const actors = Object.entries(data.actors)
        .filter(([, meta]) => meta.category === activeCategory)
        .sort((a, b) => {
            const lastA = a[1].trajectory[a[1].trajectory.length - 1] || 0;
            const lastB = b[1].trajectory[b[1].trajectory.length - 1] || 0;
            return lastB - lastA;
        })
        .filter(([name]) => {
            if (!filter) return true;
            return displayName(name, activeCategory).toLowerCase().includes(filter);
        });

    if (actors.length === 0) {
        list.innerHTML = '<div style="padding:14px 12px;font-size:0.68rem;color:rgba(255,255,255,0.2);text-align:center;">No results</div>';
        return;
    }

    list.innerHTML = actors.map(([name, meta]) => {
        const isActive = activeActors.some(a => a.name === name);
        const color    = isActive ? ACTOR_COLORS[usedColors[name]] : null;
        const dName    = displayName(name, activeCategory);
        const dotStyle = color ? `background:${color.line}` : 'background:rgba(255,255,255,0.12)';
        const lastRate = meta.trajectory[meta.trajectory.length - 1];
        const rateStr  = lastRate != null ? `${lastRate.toFixed(1)}%` : '';
        return `
            <div class="at-dd-item ${isActive ? 'active' : ''}" data-name="${name}" data-cat="${activeCategory}">
                <div class="at-dd-dot" style="${dotStyle}"></div>
                <span class="at-dd-name">${dName}</span>
                <span class="at-dd-rate">${rateStr}</span>
                <span class="at-dd-check">✓</span>
            </div>
        `;
    }).join('');

    list.querySelectorAll('.at-dd-item').forEach(item => {
        item.addEventListener('click', () => {
            toggleActor(item.dataset.name, item.dataset.cat, data);
            renderDropdownList(data, document.getElementById('at-search')?.value.trim().toLowerCase() || '');
        });
    });
}

// ════════════════════════════════════════
// ACTOR TOGGLE / ADD / REMOVE
// ════════════════════════════════════════

function toggleActor(name, category, data) {
    const existing = activeActors.findIndex(a => a.name === name);
    if (existing !== -1) {
        removeActor(name);
    } else {
        addActor(name, category, data);
    }
}

function addActor(name, category, data) {
    if (activeActors.length >= MAX_ACTORS) return;
    if (activeActors.some(a => a.name === name)) return;

    const meta = data.actors[name];
    if (!meta) return;

    const color = assignColor(name);
    const traj  = meta.trajectory;
    const currentRate = traj[traj.length - 1];

    activeActors.push({
        name,
        category,
        displayName: displayName(name, category),
        trajectory: traj,
        currentRate,
    });

    refresh(data);
}

function removeActor(name) {
    activeActors = activeActors.filter(a => a.name !== name);
    releaseColor(name);
    const data = cachedData;
    if (data) refresh(data);
}

function updateSidebarCount() {
    const el = document.getElementById('at-sidebar-count');
    if (!el) return;
    el.textContent = `${activeActors.length} / ${MAX_ACTORS}`;
    el.classList.toggle('at-count-full', activeActors.length >= MAX_ACTORS);
}

function refresh(data) {
    renderSelectedBar();
    renderChart(data);
    updateSidebarCount();
    const filter = document.getElementById('at-search')?.value.trim().toLowerCase() || '';
    renderDropdownList(data, filter);
}

// ════════════════════════════════════════
// INIT
// ════════════════════════════════════════

export async function renderActorTrajectories() {
    const data = await loadData();
    if (!data) return;

    // Period label
    const periodEl = document.getElementById('at-period');
    if (periodEl) {
        const visibleLabels = data.week_labels.slice(-DISPLAY_WEEKS);
        periodEl.textContent = `${visibleLabels[0]} → ${visibleLabels[visibleLabels.length - 1]}  ·  ${DISPLAY_WEEKS} weeks`;
    }

    // Load default actors
    for (const name of data.default_actors) {
        const meta = data.actors[name];
        if (!meta) continue;
        const color = assignColor(name);
        const traj  = meta.trajectory;
        activeActors.push({
            name,
            category: meta.category,
            displayName: displayName(name, meta.category),
            trajectory: traj,
            currentRate: traj[traj.length - 1],
        });
    }

    initSidebar(data);
    updateSidebarCount();
    renderSelectedBar();
    renderChart(data);
}
