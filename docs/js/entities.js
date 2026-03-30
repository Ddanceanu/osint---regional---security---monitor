// ════════════════════════════════════════
// ENTITIES PAGE
// Entity Explorer, Coverage Matrix, Entity Pairs
// ════════════════════════════════════════

import { CHART_COLORS, THEME_LABELS } from './constants.js';

let entityData = null;
let currentCat = 'persons';
let currentCovCat = 'persons';
let currentEntity = null;
let profileChart = null;

const SOURCE_TYPES = {
    mae: 'official', nato: 'official', eu_council: 'official', eeas: 'official',
    ecfr: 'think_tank', isw: 'think_tank', chatham_house: 'think_tank',
};

const CAT_COLORS = {
    persons: '#00CFFF',
    countries: '#7EB8FF',
    organizations: '#5EDBA0',
    locations: '#FFB87A',
};

// ════════════════════════════════════════
// ENTRY POINT
// ════════════════════════════════════════

export function renderEntitiesPage() {
    fetch('data/entity_analysis.json')
        .then(res => res.json())
        .then(data => {
            entityData = data;
            initCatTabs();
            initCoverageTabsUI();
            renderEntityList('persons');
            renderCoverageMatrix('persons');
            renderEntityPairs();
        })
        .catch(err => console.error('Failed to load entity analysis:', err));
}

// ════════════════════════════════════════
// SECTION 1: ENTITY EXPLORER
// ════════════════════════════════════════

function initCatTabs() {
    document.querySelectorAll('.en-cat-tab').forEach(btn => {
        btn.addEventListener('click', () => {
            currentCat = btn.dataset.cat;
            document.querySelectorAll('.en-cat-tab').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById('en-search').value = '';
            renderEntityList(currentCat);
            clearProfile();
        });
    });

    const search = document.getElementById('en-search');
    if (search) {
        search.addEventListener('input', () => {
            renderEntityList(currentCat, search.value.trim().toLowerCase());
        });
    }
}

function renderEntityList(cat, filter = '') {
    const container = document.getElementById('en-entity-list');
    if (!container || !entityData) return;

    const profiles = entityData.profiles[cat] || {};
    const color = CAT_COLORS[cat] || '#7A9DC0';

    let entries = Object.entries(profiles);
    if (filter) {
        entries = entries.filter(([name]) => name.toLowerCase().includes(filter));
    }

    if (entries.length === 0) {
        container.innerHTML = '<div style="padding:20px;text-align:center;color:var(--text-muted);font-size:.8rem;font-style:italic">No entities found</div>';
        return;
    }

    const maxCount = entries[0]?.[1]?.total || 1;

    container.innerHTML = entries.map(([name, profile], idx) => {
        const pct = ((profile.total / maxCount) * 100).toFixed(0);
        const isActive = name === currentEntity ? 'active' : '';
        return `<div class="en-entity-item ${isActive}" data-entity="${escapeAttr(name)}">
            <span class="en-entity-rank">${idx + 1}</span>
            <span class="en-entity-name">${escapeHtml(name)}</span>
            <div class="en-entity-bar-mini-wrap">
                <div class="en-entity-bar-mini" style="width:${pct}%; background:${color}80"></div>
            </div>
            <span class="en-entity-count-badge">${profile.total}</span>
        </div>`;
    }).join('');

    container.querySelectorAll('.en-entity-item').forEach(item => {
        item.addEventListener('click', () => {
            const name = item.dataset.entity;
            currentEntity = name;
            container.querySelectorAll('.en-entity-item').forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            const profile = profiles[name];
            if (profile) renderEntityProfile(name, profile, cat);
        });
    });

    // Auto-select first entity if none is currently active
    if (!currentEntity) {
        const first = container.querySelector('.en-entity-item');
        if (first) first.click();
    }
}

function clearProfile() {
    currentEntity = null;
    const el = document.getElementById('en-profile');
    if (el) el.innerHTML = '<div class="en-profile-placeholder">Select an entity from the list</div>';
    if (profileChart) { profileChart.destroy(); profileChart = null; }
}

function renderEntityProfile(name, profile, cat) {
    const container = document.getElementById('en-profile');
    if (!container) return;

    if (profileChart) { profileChart.destroy(); profileChart = null; }

    const color = CAT_COLORS[cat] || '#7A9DC0';
    const topThemes = profile.themes.slice(0, 5);
    const topSources = profile.sources.slice(0, 7);
    const maxThemeCount = topThemes[0]?.count || 1;
    const maxSourceCount = topSources[0]?.count || 1;

    const themesHtml = topThemes.map(t => {
        const themeColor = CHART_COLORS[t.theme_key] || '#7A9DC0';
        const barPct = ((t.count / maxThemeCount) * 100).toFixed(0);
        return `<div class="en-theme-item">
            <span class="en-theme-dot" style="background:${themeColor}"></span>
            <span class="en-theme-name">${t.label}</span>
            <div class="en-theme-bar-wrap">
                <div class="en-theme-bar" style="width:${barPct}%; background:${themeColor}80"></div>
            </div>
            <span class="en-theme-pct">${t.share}%</span>
        </div>`;
    }).join('');

    const sourcesHtml = topSources.map(s => {
        const barPct = ((s.count / maxSourceCount) * 100).toFixed(0);
        const stype = SOURCE_TYPES[s.source_key] || 'official';
        return `<div class="en-source-item">
            <span class="en-source-dot ${stype}"></span>
            <span class="en-source-name-small">${s.source_name}</span>
            <div class="en-source-bar-wrap">
                <div class="en-source-bar-fill" style="width:${barPct}%; background:${color}60"></div>
            </div>
            <span class="en-source-count-small">${s.count}</span>
        </div>`;
    }).join('');

    container.innerHTML = `
        <div class="en-profile-inner">
            <div class="en-profile-header">
                <div class="en-profile-name">${escapeHtml(name)}</div>
                <div class="en-profile-kpis">
                    <div class="en-kpi">
                        <div class="en-kpi-value">${profile.total}</div>
                        <div class="en-kpi-label">Documents</div>
                    </div>
                    <div class="en-kpi">
                        <div class="en-kpi-value">${profile.doc_rate}%</div>
                        <div class="en-kpi-label">Of Corpus</div>
                    </div>
                    <div class="en-kpi">
                        <div class="en-kpi-value">${profile.sources.length}</div>
                        <div class="en-kpi-label">Sources</div>
                    </div>
                </div>
            </div>
            <div class="en-profile-grid">
                <div class="en-sub-card en-sub-card-full">
                    <div class="en-sub-title">Weekly Mention Timeline</div>
                    <div class="en-timeline-wrap">
                        <canvas id="en-profile-chart"></canvas>
                    </div>
                </div>
                <div class="en-sub-card">
                    <div class="en-sub-title">Thematic Context</div>
                    ${themesHtml || '<div style="color:var(--text-muted);font-size:.75rem;font-style:italic">No theme data</div>'}
                </div>
                <div class="en-sub-card">
                    <div class="en-sub-title">Source Coverage</div>
                    ${sourcesHtml || '<div style="color:var(--text-muted);font-size:.75rem;font-style:italic">No source data</div>'}
                </div>
            </div>
        </div>
    `;

    drawProfileTimeline(profile.timeline, color);
}

function drawProfileTimeline(timeline, color) {
    const canvas = document.getElementById('en-profile-chart');
    if (!canvas) return;

    const labels = timeline.map(w => w.week_label);
    const values = timeline.map(w => w.count);

    profileChart = new Chart(canvas, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Mentions',
                data: values,
                backgroundColor: color + '55',
                borderColor: color,
                borderWidth: 1,
                borderRadius: 2,
                barPercentage: 0.75,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: '#0d1b2a',
                    borderColor: '#1e3a5f',
                    borderWidth: 1,
                    titleFont: { size: 9, family: "'IBM Plex Mono', monospace" },
                    bodyFont: { size: 9, family: "'IBM Plex Mono', monospace" },
                    callbacks: { label: ctx => `${ctx.parsed.y} docs` }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#5a6577', font: { size: 7 }, maxRotation: 45, maxTicksLimit: 10 },
                    grid: { display: false }
                },
                y: {
                    beginAtZero: true,
                    ticks: { color: '#5a6577', font: { size: 7 }, precision: 0 },
                    grid: { color: 'rgba(30, 58, 95, 0.3)', drawBorder: false }
                }
            }
        }
    });
}

// ════════════════════════════════════════
// SECTION 2: COVERAGE MATRIX
// ════════════════════════════════════════

function initCoverageTabsUI() {
    document.querySelectorAll('.en-cov-tab').forEach(btn => {
        btn.addEventListener('click', () => {
            currentCovCat = btn.dataset.cat;
            document.querySelectorAll('.en-cov-tab').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            renderCoverageMatrix(currentCovCat);
        });
    });
}

function renderCoverageMatrix(cat) {
    const wrap = document.getElementById('en-coverage-wrap');
    if (!wrap || !entityData) return;

    const matData = entityData.coverage_matrix[cat];
    if (!matData) { wrap.innerHTML = '<div style="color:var(--text-muted);font-size:.8rem;padding:20px">No data</div>'; return; }

    const { entities, sources, source_keys, rows, max_value } = matData;
    const color = CAT_COLORS[cat] || '#7A9DC0';

    let html = `<table class="en-cov-table">
        <thead><tr>
            <th class="en-cov-entity-hd">Entity</th>
            ${sources.map(s => `<th>${s}</th>`).join('')}
        </tr></thead>
        <tbody>`;

    for (const row of rows) {
        html += `<tr class="en-cov-row">
            <td class="en-cov-entity-cell">${escapeHtml(row.entity)}</td>
            ${row.counts.map((cnt, i) => {
                if (cnt === 0) {
                    return `<td class="en-cov-data-cell"><div class="en-cov-cell-inner en-cov-cell-zero">—</div></td>`;
                }
                const intensity = max_value > 0 ? cnt / max_value : 0;
                const alpha = (0.12 + intensity * 0.65).toFixed(2);
                const textAlpha = (0.4 + intensity * 0.6).toFixed(2);
                return `<td class="en-cov-data-cell" title="${sources[i]}: ${cnt} docs mentioning ${row.entity}">
                    <div class="en-cov-cell-inner" style="background:rgba(${hexToRgb(color)},${alpha}); color:rgba(255,255,255,${textAlpha})">${cnt}</div>
                </td>`;
            }).join('')}
        </tr>`;
    }

    html += '</tbody></table>';
    wrap.innerHTML = html;
}

// ════════════════════════════════════════
// SECTION 3: ENTITY PAIRS
// ════════════════════════════════════════

function renderEntityPairs() {
    const container = document.getElementById('en-pairs-body');
    if (!container || !entityData) return;

    const pairs = entityData.entity_pairs || [];
    if (pairs.length === 0) {
        container.innerHTML = '<div style="color:var(--text-muted);font-size:.8rem;font-style:italic;padding:20px">No pair data available</div>';
        return;
    }

    const maxCount = pairs[0].count;

    container.innerHTML = pairs.map((pair, idx) => {
        const barPct = ((pair.count / maxCount) * 100).toFixed(0);
        const catA = pair.category_a.replace('s', '').slice(0, 3).toUpperCase();
        const catB = pair.category_b.replace('s', '').slice(0, 3).toUpperCase();

        return `<div class="en-pair-item">
            <span class="en-pair-rank">${idx + 1}.</span>
            <div class="en-pair-entities">
                <span class="en-pair-name">${escapeHtml(pair.entity_a)}</span>
                <span class="en-pair-sep">+</span>
                <span class="en-pair-name">${escapeHtml(pair.entity_b)}</span>
            </div>
            <div class="en-pair-cats">
                <span class="en-pair-cat-badge">${catA}</span>
                <span class="en-pair-cat-badge">${catB}</span>
            </div>
            <span class="en-pair-count">${pair.count}</span>
            <div class="en-pair-bar-wrap">
                <div class="en-pair-bar" style="width:${barPct}%"></div>
            </div>
        </div>`;
    }).join('');
}

// ════════════════════════════════════════
// HELPERS
// ════════════════════════════════════════

function hexToRgb(hex) {
    if (!hex || hex.length < 7) return '59,123,255';
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `${r},${g},${b}`;
}

function escapeHtml(str) {
    const d = document.createElement('div');
    d.textContent = str || '';
    return d.innerHTML;
}

function escapeAttr(str) {
    return (str || '').replace(/"/g, '&quot;');
}
