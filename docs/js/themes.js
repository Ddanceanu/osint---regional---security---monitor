// ════════════════════════════════════════
// THEMES PAGE
// Theme Explorer, Co-occurrence Matrix, Concentration
// ════════════════════════════════════════

import { THEME_LABELS, CHART_COLORS, THEME_SHIFT_COLORS } from './constants.js';

let themeAnalysisData = null;
let themeTimelineChart = null;

// ════════════════════════════════════════
// ENTRY POINT
// ════════════════════════════════════════

export function renderThemesPage() {
    fetch('data/theme_analysis.json')
        .then(res => res.json())
        .then(data => {
            themeAnalysisData = data;
            renderThemeSelector(data);
            renderCooccurrenceMatrix(data.cooccurrence);
            renderConcentration(data.concentration);

            // Auto-select the largest theme
            const themes = data.themes;
            let largest = null;
            let maxCount = 0;
            for (const [key, profile] of Object.entries(themes)) {
                if (key !== 'other_mixed' && profile.document_count > maxCount) {
                    maxCount = profile.document_count;
                    largest = key;
                }
            }
            if (largest) selectTheme(largest);
        })
        .catch(err => console.error('Failed to load theme analysis:', err));
}

// ════════════════════════════════════════
// THEME SELECTOR
// ════════════════════════════════════════

function renderThemeSelector(data) {
    const container = document.getElementById('th-selector');
    if (!container) return;

    const themeOrder = [
        'support_ukraine',
        'eastern_flank_nato_deterrence',
        'romania_republic_of_moldova',
        'russia_regional_implications',
        'eu_regional_security',
        'black_sea_regional_security',
        'other_mixed',
    ];

    container.innerHTML = themeOrder.map(key => {
        const profile = data.themes[key];
        if (!profile) return '';
        const label = THEME_LABELS[key] || key;
        const color = CHART_COLORS[key] || '#7A9DC0';
        return `<button class="th-selector-btn" data-theme="${key}">
            <span class="th-selector-dot" style="background:${color}"></span>
            <span class="th-selector-label">${label}</span>
            <span class="th-selector-count">${profile.document_count}</span>
        </button>`;
    }).join('');

    container.querySelectorAll('.th-selector-btn').forEach(btn => {
        btn.addEventListener('click', () => selectTheme(btn.dataset.theme));
    });
}

function selectTheme(themeKey) {
    // Update active button
    document.querySelectorAll('.th-selector-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.theme === themeKey);
    });

    const profile = themeAnalysisData.themes[themeKey];
    if (!profile) return;

    renderThemeDetail(themeKey, profile);
}

// ════════════════════════════════════════
// THEME DETAIL
// ════════════════════════════════════════

function renderThemeDetail(themeKey, profile) {
    const container = document.getElementById('th-detail');
    if (!container) return;

    const color = CHART_COLORS[themeKey] || '#7A9DC0';
    const barColor = THEME_SHIFT_COLORS[themeKey] || '#5C6B7E';
    const sourcesCount = profile.source_breakdown.length;

    container.innerHTML = `
        <!-- Header -->
        <div class="th-detail-header">
            <div class="th-detail-title-group">
                <div class="th-detail-color-bar" style="background:${color}"></div>
                <div class="th-detail-theme-name">${profile.label}</div>
            </div>
            <div class="th-detail-kpis">
                <div class="th-kpi">
                    <div class="th-kpi-value">${profile.document_count}</div>
                    <div class="th-kpi-label">Documents</div>
                </div>
                <div class="th-kpi">
                    <div class="th-kpi-value">${profile.percentage}%</div>
                    <div class="th-kpi-label">Of Corpus</div>
                </div>
                <div class="th-kpi">
                    <div class="th-kpi-value">${sourcesCount}</div>
                    <div class="th-kpi-label">Sources</div>
                </div>
            </div>
        </div>

        <!-- Body -->
        <div class="th-detail-body">
            <!-- Timeline (full width) -->
            <div class="th-sub-card th-timeline-card">
                <div class="th-sub-card-header">
                    <span class="th-sub-card-title">Weekly Document Volume</span>
                </div>
                <div class="th-timeline-chart-wrap">
                    <canvas id="th-timeline-canvas"></canvas>
                </div>
            </div>

            <!-- Top Entities (full width) -->
            <div class="th-sub-card th-entities-card">
                <div class="th-sub-card-header">
                    <span class="th-sub-card-title">Key Entities in This Theme</span>
                </div>
                <div class="th-entities-grid">
                    ${buildEntityColumn('Persons', profile.top_entities.persons, color)}
                    ${buildEntityColumn('Countries', profile.top_entities.countries, color)}
                    ${buildEntityColumn('Organizations', profile.top_entities.organizations, color)}
                </div>
            </div>

            <!-- Source Breakdown -->
            <div class="th-sub-card">
                <div class="th-sub-card-header">
                    <span class="th-sub-card-title">Source Composition</span>
                </div>
                ${buildSourceBreakdown(profile.source_breakdown)}
            </div>

            <!-- Recent Documents -->
            <div class="th-sub-card">
                <div class="th-sub-card-header">
                    <span class="th-sub-card-title">Recent Documents</span>
                </div>
                ${buildRecentDocs(profile.recent_documents)}
            </div>
        </div>
    `;

    drawThemeTimeline(profile.timeline, barColor, color);
}

function buildEntityColumn(title, entities, color) {
    if (!entities || entities.length === 0) {
        return `<div>
            <div class="th-entity-col-title">${title}</div>
            <div class="th-entity-empty">No data</div>
        </div>`;
    }

    const maxCount = entities[0].count;
    const items = entities.map(e => {
        const pct = maxCount > 0 ? ((e.count / maxCount) * 100).toFixed(0) : 0;
        return `<div class="th-entity-item">
            <span class="th-entity-name">${e.name}</span>
            <div class="th-entity-bar-wrap">
                <div class="th-entity-bar" style="width:${pct}%; background:${color}; opacity:0.5"></div>
            </div>
            <span class="th-entity-count">${e.count}</span>
        </div>`;
    }).join('');

    return `<div>
        <div class="th-entity-col-title">${title}</div>
        ${items}
    </div>`;
}

function buildSourceBreakdown(sources) {
    if (!sources || sources.length === 0) return '<div class="th-entity-empty">No sources</div>';

    return sources.map(s => {
        return `<div class="th-source-item">
            <span class="th-source-type-dot ${s.source_type}"></span>
            <span class="th-source-name">${s.source_name}</span>
            <div class="th-source-bar-wrap">
                <div class="th-source-bar ${s.source_type}" style="width:${s.percentage}%"></div>
            </div>
            <span class="th-source-pct">${s.percentage}%</span>
        </div>`;
    }).join('');
}

function buildRecentDocs(docs) {
    if (!docs || docs.length === 0) return '<div class="th-entity-empty">No documents</div>';

    return docs.map(d => {
        const dateStr = d.date ? new Date(d.date + 'T00:00:00').toLocaleDateString('en-GB', {
            day: 'numeric', month: 'short'
        }) : '';
        const link = d.url
            ? `<a href="${d.url}" target="_blank" rel="noopener">${escapeHtml(d.title)}</a>`
            : escapeHtml(d.title);
        return `<div class="th-recent-item">
            <span class="th-recent-date">${dateStr}</span>
            <span class="th-recent-source">${d.source_name}</span>
            <span class="th-recent-title">${link}</span>
        </div>`;
    }).join('');
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// ════════════════════════════════════════
// THEME TIMELINE CHART
// ════════════════════════════════════════

function drawThemeTimeline(timeline, barColor, lineColor) {
    const canvas = document.getElementById('th-timeline-canvas');
    if (!canvas) return;

    if (themeTimelineChart) {
        themeTimelineChart.destroy();
        themeTimelineChart = null;
    }

    const labels = timeline.map(w => w.week_label);
    const values = timeline.map(w => w.count);

    themeTimelineChart = new Chart(canvas, {
        type: 'bar',
        data: {
            labels,
            datasets: [{
                label: 'Documents',
                data: values,
                backgroundColor: barColor + 'AA',
                borderColor: lineColor,
                borderWidth: 1,
                borderRadius: 3,
                barPercentage: 0.7,
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
                    titleFont: { size: 10, family: "'IBM Plex Mono', monospace" },
                    bodyFont: { size: 10, family: "'IBM Plex Mono', monospace" },
                    callbacks: {
                        label: ctx => `${ctx.parsed.y} documents`
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: '#5a6577',
                        font: { size: 8, family: "'JetBrains Mono', monospace" },
                        maxRotation: 45,
                        maxTicksLimit: 12,
                    },
                    grid: { display: false }
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#5a6577',
                        font: { size: 8, family: "'JetBrains Mono', monospace" },
                        precision: 0,
                    },
                    grid: { color: 'rgba(30, 58, 95, 0.3)', drawBorder: false }
                }
            }
        }
    });
}

// ════════════════════════════════════════
// CO-OCCURRENCE MATRIX
// ════════════════════════════════════════

function renderCooccurrenceMatrix(coData) {
    const wrap = document.getElementById('th-matrix-wrap');
    const meta = document.getElementById('th-cooccurrence-meta');
    if (!wrap) return;

    const { keys, labels, matrix, max_value, total_with_secondary, total_documents } = coData;
    const n = keys.length;
    const pctWithSec = total_documents > 0
        ? ((total_with_secondary / total_documents) * 100).toFixed(0)
        : 0;

    if (meta) {
        meta.textContent = `${total_with_secondary} of ${total_documents} docs (${pctWithSec}%) have secondary themes`;
    }

    // Short labels for column headers
    const SHORT_LABELS = {
        'support_ukraine': 'Ukraine',
        'eastern_flank_nato_deterrence': 'NATO Flank',
        'romania_republic_of_moldova': 'RO-MD',
        'russia_regional_implications': 'Russia',
        'eu_regional_security': 'EU Security',
        'black_sea_regional_security': 'Black Sea',
    };

    // Medium labels for row headers (readable but compact)
    const ROW_LABELS = {
        'support_ukraine': 'Support for Ukraine',
        'eastern_flank_nato_deterrence': 'Eastern Flank / NATO',
        'romania_republic_of_moldova': 'Romania & Moldova',
        'russia_regional_implications': 'Russia Regional',
        'eu_regional_security': 'EU Regional Security',
        'black_sea_regional_security': 'Black Sea Security',
    };

    // Fixed grid: generous row header + equal data columns
    const cols = `200px repeat(${n}, minmax(60px, 1fr))`;

    let html = `<div class="th-matrix" style="grid-template-columns:${cols}">`;

    // Top-left corner — label
    html += `<div class="th-matrix-corner" style="font-family:var(--font-mono);font-size:.5rem;color:rgba(255,255,255,0.2);padding:4px 0;text-align:right;align-self:end">MAIN \\ SECONDARY</div>`;

    // Column headers (short, horizontal)
    for (let c = 0; c < n; c++) {
        const shortLabel = SHORT_LABELS[keys[c]] || labels[c];
        const color = CHART_COLORS[keys[c]] || '#7A9DC0';
        html += `<div class="th-matrix-col-hd" style="color:${color}" title="${labels[c]}">${shortLabel}</div>`;
    }

    // Rows
    for (let r = 0; r < n; r++) {
        const rowColor = CHART_COLORS[keys[r]] || '#7A9DC0';

        const rowLabel = ROW_LABELS[keys[r]] || labels[r];
        html += `<div class="th-matrix-row-hd" title="${labels[r]}">
            <span class="th-matrix-row-dot" style="background:${rowColor}"></span>
            ${rowLabel}
        </div>`;

        for (let c = 0; c < n; c++) {
            const val = matrix[r][c];

            if (val === null) {
                html += `<div class="th-matrix-cell diagonal">—</div>`;
            } else if (val === 0) {
                html += `<div class="th-matrix-cell zero" title="${labels[r]} + ${labels[c]}: 0">0</div>`;
            } else {
                const intensity = max_value > 0 ? val / max_value : 0;
                const alpha = 0.1 + intensity * 0.7;
                const textAlpha = 0.4 + intensity * 0.6;
                const rowCol = CHART_COLORS[keys[r]] || '#7A9DC0';
                html += `<div class="th-matrix-cell"
                    style="background:rgba(${hexToRgb(rowCol)},${alpha.toFixed(2)}); color:rgba(255,255,255,${textAlpha.toFixed(2)})"
                    title="${labels[r]} (main) + ${labels[c]} (secondary): ${val} docs">
                    ${val}
                </div>`;
            }
        }
    }

    html += '</div>';
    wrap.innerHTML = html;
}

function hexToRgb(hex) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `${r},${g},${b}`;
}

// ════════════════════════════════════════
// THEME CONCENTRATION
// ════════════════════════════════════════

function renderConcentration(concentration) {
    const grid = document.getElementById('th-concentration-grid');
    if (!grid) return;

    const themeOrder = [
        'support_ukraine',
        'eastern_flank_nato_deterrence',
        'romania_republic_of_moldova',
        'russia_regional_implications',
        'eu_regional_security',
        'black_sea_regional_security',
        'other_mixed',
    ];

    // Header row
    let html = `<div class="th-conc-header-row">
        <span class="th-conc-col-hd">Source</span>
        <span class="th-conc-col-hd">Theme Distribution</span>
        <span class="th-conc-col-hd th-conc-col-hd-right">Dominant</span>
        <span class="th-conc-col-hd th-conc-col-hd-center" title="Number of themes with >5% share">DIV</span>
    </div>`;

    // Source rows
    for (const src of concentration) {
        // Stacked bar segments
        let barHtml = '';
        for (const tk of themeOrder) {
            const td = src.theme_distribution[tk];
            if (!td || td.share === 0) continue;
            const color = THEME_SHIFT_COLORS[tk] || '#5C6B7E';
            const label = THEME_LABELS[tk] || tk;
            barHtml += `<div class="th-conc-bar-seg" style="width:${td.share}%; background:${color}"
                title="${label}: ${td.count} docs (${td.share}%)"></div>`;
        }

        // Diversity class
        let divClass = 'low';
        if (src.diversity_index >= 4) divClass = 'high';
        else if (src.diversity_index >= 3) divClass = 'mid';

        const dominantPct = src.dominant_share.toFixed(0) + '%';

        html += `<div class="th-conc-row">
            <div class="th-conc-source">
                <span class="th-conc-source-dot ${src.source_type}"></span>
                <span class="th-conc-source-name">${src.source_name}</span>
                <span class="th-conc-source-count">${src.total_docs}</span>
            </div>
            <div class="th-conc-bar-wrap">${barHtml}</div>
            <span class="th-conc-dominant">${dominantPct}</span>
            <span class="th-conc-diversity ${divClass}" title="${src.diversity_index} themes with >5% share">${src.diversity_index}</span>
        </div>`;
    }

    // Legend
    html += `<div class="th-conc-legend">`;
    for (const tk of themeOrder) {
        const color = THEME_SHIFT_COLORS[tk] || '#5C6B7E';
        const label = THEME_LABELS[tk] || tk;
        html += `<div class="th-conc-legend-item">
            <span class="th-conc-legend-swatch" style="background:${color}"></span>
            <span class="th-conc-legend-label">${label}</span>
        </div>`;
    }
    html += '</div>';

    grid.innerHTML = html;
}
