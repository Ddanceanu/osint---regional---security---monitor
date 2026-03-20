// ════════════════════════════════════════
// CONSTANTS
// ════════════════════════════════════════

const THEME_LABELS = {
    support_ukraine:               "Support for Ukraine",
    eastern_flank_nato_deterrence: "Eastern Flank NATO",
    romania_republic_of_moldova:   "Romania & Moldova",
    russia_regional_implications:  "Russia Regional",
    eu_regional_security:          "EU Regional Security",
    black_sea_regional_security:   "Black Sea Security",
    other_mixed:                   "Other / Mixed",
};

const THEME_BADGES = {
    support_ukraine:               { bg: "#0C1E4A", text: "#7EB8FF", border: "#1A3C8A" },
    eastern_flank_nato_deterrence: { bg: "#1C0E50", text: "#B8A8FF", border: "#3D2290" },
    romania_republic_of_moldova:   { bg: "#3A1505", text: "#FFB87A", border: "#8A3A10" },
    russia_regional_implications:  { bg: "#3A0808", text: "#FF9494", border: "#8A2020" },
    eu_regional_security:          { bg: "#051E14", text: "#5EDBA0", border: "#0D5034" },
    black_sea_regional_security:   { bg: "#051828", text: "#60CCFF", border: "#0A4070" },
    other_mixed:                   { bg: "#111824", text: "#7A9DC0", border: "#223040" },
};

// ════════════════════════════════════════
// STATE
// ════════════════════════════════════════

let allDocuments = [];
let filteredDocuments = [];

const state = {
    search:        "",
    sources:       new Set(),
    themes:        new Set(),
    countries:     new Set(),
    organizations: new Set(),
    dateFrom:      "",
    dateTo:        "",
};

// ════════════════════════════════════════
// NAVIGATION
// ════════════════════════════════════════

const pageSubtitles = {
    explorer: 'Document Explorer — analysis workspace',
    overview: 'Corpus summary and analytical context',
    themes: 'Thematic breakdown and trend analysis',
    entities: 'Actors, locations and organizations across the corpus'
};

document.querySelectorAll('.nav-tab').forEach(tab => {
    tab.addEventListener('click', () => {
        const targetPage = tab.dataset.page;
        document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
        tab.classList.add('active');
        document.getElementById('page-' + targetPage).classList.add('active');
        const subtitleEl = document.getElementById('page-subtitle');
        if (subtitleEl && pageSubtitles[targetPage]) subtitleEl.textContent = pageSubtitles[targetPage];
    });
});

// ════════════════════════════════════════
// TIMESTAMP
// ════════════════════════════════════════

function updateTimestamp() {
    const now = new Date();
    const formatted = now.toISOString().slice(0, 16).replace('T', ' ') + ' UTC';
    const ts = document.getElementById('explorer-timestamp');
    if (ts) ts.textContent = formatted;
}

updateTimestamp();

// ════════════════════════════════════════
// LOAD DOCUMENTS
// ════════════════════════════════════════

async function loadDocuments() {
    try {
        console.log('Fetching documents...');
        const response = await fetch('data/documents.json');
        allDocuments = await response.json();
        console.log('Documents loaded:', allDocuments.length);

        initFilters();
        applyFilters();
        renderTable(filteredDocuments);
        renderKPIs(filteredDocuments);
        renderDatasetStrip();
        renderOverview(allDocuments);

    } catch (error) {
        console.error('Failed to load documents:', error);
        document.getElementById('table-body').innerHTML =
            '<tr><td colspan="8" class="table-loading">Failed to load documents. Make sure the server is running.</td></tr>';
    }
}

// ════════════════════════════════════════
// FILTER INIT
// ════════════════════════════════════════

function initFilters() {
    const sources      = [...new Set(allDocuments.map(d => d.source_name).filter(Boolean))].sort();
    const themeKeys    = [...new Set(allDocuments.map(d => d.main_theme).filter(Boolean))];
    const allCountries = [...new Set(allDocuments.flatMap(d => d.entities?.countries || []))].sort();
    const allOrgs      = [...new Set(allDocuments.flatMap(d => d.entities?.organizations || []))].sort();

    // Default: sources and themes all selected, countries/orgs none
    sources.forEach(s => state.sources.add(s));
    themeKeys.forEach(t => state.themes.add(t));

    // Dates
    const dates = allDocuments.map(d => d.publication_date_iso).filter(Boolean).sort();
    if (dates.length) {
        state.dateFrom = dates[0];
        state.dateTo   = dates[dates.length - 1];
        document.getElementById('date-from').value = state.dateFrom;
        document.getElementById('date-to').value   = state.dateTo;
    }

    // Build checklists
    buildChecklist('source-list', sources, state.sources, true);
    buildChecklist('theme-list',  themeKeys, state.themes, true, k => THEME_LABELS[k] || k);
    buildChecklist('country-list', allCountries, state.countries, false);
    buildChecklist('org-list',     allOrgs,      state.organizations, false);

    // Search
    document.getElementById('search-input').addEventListener('input', e => {
        state.search = e.target.value;
        refresh();
    });

    // Dates
    document.getElementById('date-from').addEventListener('change', e => {
        state.dateFrom = e.target.value;
        refresh();
    });

    document.getElementById('date-to').addEventListener('change', e => {
        state.dateTo = e.target.value;
        refresh();
    });
}

function buildChecklist(containerId, items, selectedSet, defaultChecked, labelFn = null) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.innerHTML = '';

    items.forEach(item => {
        const label     = labelFn ? labelFn(item) : item;
        const isChecked = defaultChecked ? true : selectedSet.has(item);
        if (isChecked) selectedSet.add(item);

        const el = document.createElement('div');
        el.className = 'check-item' + (isChecked ? ' checked' : '');
        el.innerHTML = `
            <div class="check-box">${isChecked ? '✓' : ''}</div>
            <span>${escapeHtml(label)}</span>
        `;

        el.addEventListener('click', () => {
            if (selectedSet.has(item)) {
                selectedSet.delete(item);
                el.classList.remove('checked');
                el.querySelector('.check-box').textContent = '';
            } else {
                selectedSet.add(item);
                el.classList.add('checked');
                el.querySelector('.check-box').textContent = '✓';
            }
            refresh();
        });

        container.appendChild(el);
    });
}

function refresh() {
    applyFilters();
    renderTable(filteredDocuments);
    renderKPIs(filteredDocuments);
}

// ════════════════════════════════════════
// RESET FILTERS
// ════════════════════════════════════════

function resetFilters() {
    state.search = '';
    state.countries.clear();
    state.organizations.clear();

    const allSources  = [...new Set(allDocuments.map(d => d.source_name).filter(Boolean))];
    const allThemes   = [...new Set(allDocuments.map(d => d.main_theme).filter(Boolean))];
    state.sources.clear();
    allSources.forEach(s => state.sources.add(s));
    state.themes.clear();
    allThemes.forEach(t => state.themes.add(t));

    const dates = allDocuments.map(d => d.publication_date_iso).filter(Boolean).sort();
    if (dates.length) {
        state.dateFrom = dates[0];
        state.dateTo   = dates[dates.length - 1];
    }

    document.getElementById('search-input').value = '';
    document.getElementById('date-from').value    = state.dateFrom;
    document.getElementById('date-to').value      = state.dateTo;

    buildChecklist('source-list',  [...new Set(allDocuments.map(d => d.source_name).filter(Boolean))].sort(), state.sources, true);
    buildChecklist('theme-list',   [...new Set(allDocuments.map(d => d.main_theme).filter(Boolean))], state.themes, true, k => THEME_LABELS[k] || k);
    buildChecklist('country-list', [...new Set(allDocuments.flatMap(d => d.entities?.countries || []))].sort(), state.countries, false);
    buildChecklist('org-list',     [...new Set(allDocuments.flatMap(d => d.entities?.organizations || []))].sort(), state.organizations, false);

    refresh();
}

// ════════════════════════════════════════
// APPLY FILTERS
// ════════════════════════════════════════

function applyFilters() {
    filteredDocuments = allDocuments.filter(doc => {
        if (state.search.trim()) {
            const term = state.search.trim().toLowerCase();
            const inTitle   = (doc.title || '').toLowerCase().includes(term);
            const inContent = (doc.content || '').toLowerCase().includes(term);
            if (!inTitle && !inContent) return false;
        }

        if (state.sources.size > 0 && !state.sources.has(doc.source_name)) return false;
        if (state.themes.size > 0  && !state.themes.has(doc.main_theme))   return false;

        if (state.dateFrom && doc.publication_date_iso && doc.publication_date_iso < state.dateFrom) return false;
        if (state.dateTo   && doc.publication_date_iso && doc.publication_date_iso > state.dateTo)   return false;

        if (state.countries.size > 0) {
            const docCountries = doc.entities?.countries || [];
            if (![...state.countries].some(c => docCountries.includes(c))) return false;
        }

        if (state.organizations.size > 0) {
            const docOrgs = doc.entities?.organizations || [];
            if (![...state.organizations].some(o => docOrgs.includes(o))) return false;
        }

        return true;
    });
}

// ════════════════════════════════════════
// KPI CARDS
// ════════════════════════════════════════

function renderKPIs(docs) {
    const sources = new Set(docs.map(d => d.source_name).filter(Boolean));
    const themes  = new Set(docs.map(d => d.main_theme).filter(Boolean));
    const orgs    = new Set(docs.flatMap(d => d.entities?.organizations || []).filter(Boolean));

    const items = [
        { abbr: "DOC", value: docs.length,  label: "Total Documents", accent: "#3B7BFF", glow: "rgba(59,123,255,0.18)"  },
        { abbr: "SRC", value: sources.size, label: "Sources",         accent: "#00CFFF", glow: "rgba(0,207,255,0.15)"   },
        { abbr: "THM", value: themes.size,  label: "Main Themes",     accent: "#A78BFA", glow: "rgba(167,139,250,0.15)" },
        { abbr: "ORG", value: orgs.size,    label: "Organizations",   accent: "#34D399", glow: "rgba(52,211,153,0.15)"  },
    ];

    const grid = document.getElementById('kpi-grid');
    if (!grid) return;

    grid.innerHTML = items.map(item => `
        <div class="kpi-card" style="border-top:2px solid ${item.accent};">
            <div class="kpi-abbr" style="color:${item.accent};border-color:${item.accent};">${item.abbr}</div>
            <div class="kpi-value" style="color:${item.accent};">${item.value}</div>
            <div class="kpi-label">${item.label}</div>
            <div class="kpi-glow" style="background:${item.glow};"></div>
        </div>
    `).join('');
}

// ════════════════════════════════════════
// DATASET STRIP
// ════════════════════════════════════════

function renderDatasetStrip() {
    const dates = allDocuments.map(d => d.publication_date_iso).filter(Boolean).sort();
    const dateRange = dates.length ? `${dates[0]} → ${dates[dates.length - 1]}` : 'N/A';

    const strip = document.getElementById('dataset-strip');
    if (!strip) return;

    strip.innerHTML = `
        <div class="ds-item"><span>Documents</span><span class="ds-val">${allDocuments.length}</span></div>
        <div class="ds-sep"></div>
        <div class="ds-item"><span>Date range</span><span class="ds-val">${dateRange}</span></div>
        <div class="ds-sep"></div>
        <div class="ds-item"><span>Source</span><span class="ds-val">documents.json</span></div>
    `;
}

// ════════════════════════════════════════
// TABLE RENDER
// ════════════════════════════════════════

function renderTable(docs) {
    const tbody = document.getElementById('table-body');
    if (!tbody) return;

    if (!docs.length) {
        tbody.innerHTML = '<tr><td colspan="8" class="table-loading">No documents match the current filters.</td></tr>';
        return;
    }

    tbody.innerHTML = docs.map((doc, index) => {
        const rowClass  = 'doc-row' + (index % 2 === 1 ? ' doc-row-alt' : '');
        const rowId     = `row-${index}`;
        const detailId  = `detail-${index}`;
        const themeKey  = doc.main_theme || 'other_mixed';
        const secKeys   = doc.secondary_themes || [];
        const entities  = doc.entities || {};
        const countries = entities.countries      || [];
        const orgs      = entities.organizations  || [];
        const persons   = entities.persons        || [];
        const locations = entities.locations      || [];
        const content   = doc.content || '';
        const url       = doc.url || '';
        const date      = doc.publication_date_iso || '—';
        const source    = doc.source_name || '—';
        const title     = doc.title || '—';
        const srcType   = doc.source_type || '';

        const previewText  = buildPreview(content, 140);
        const mainBadge    = themeBadgeHtml(themeKey);
        const secBadges    = secKeys.length
            ? secKeys.slice(0, 2).map(k => themeBadgeHtml(k)).join('')
              + (secKeys.length > 2 ? `<span class="entity-more">+${secKeys.length - 2}</span>` : '')
            : '<span class="cell-muted">—</span>';

        const countryPills = pillsHtml(countries, 2);
        const orgPills     = pillsHtml(orgs, 2);

        const sourceLink = url
            ? `<a class="detail-link" href="${escapeHtml(url)}" target="_blank">↗ Open source</a>`
            : '';

        const allSecBadges      = secKeys.length ? secKeys.map(k => themeBadgeHtml(k)).join('') : '<span class="cell-muted">—</span>';
        const allCountryPills   = entityPillsAll(countries);
        const allOrgPills       = entityPillsAll(orgs);
        const allPersonPills    = entityPillsAll(persons);
        const allLocationPills  = entityPillsAll(locations);

        const contentFull = content
            ? escapeHtml(content.slice(0, 1500)) + (content.length > 1500 ? '...' : '')
            : '—';

        return `
        <tr id="${rowId}" class="${rowClass}" onclick="toggleDetail('${rowId}','${detailId}')">
            <td><span class="date-mono">${escapeHtml(date)}</span></td>
            <td><span class="source-tag">${escapeHtml(source)}</span></td>
            <td>
                <span class="title-text">${escapeHtml(title)}</span>
                <span class="expand-indicator">▶</span>
            </td>
            <td>${mainBadge}</td>
            <td>${secBadges}</td>
            <td>${countryPills}</td>
            <td>${orgPills}</td>
            <td><span class="preview-text">${escapeHtml(previewText)}</span></td>
        </tr>
        <tr id="${detailId}" class="detail-row">
            <td colspan="8" style="padding:0;border-bottom:2px solid #1A3A6A;">
                <div class="detail-panel">
                    <div class="detail-header">
                        <div class="detail-title">${escapeHtml(title)}</div>
                        <button class="close-btn" onclick="event.stopPropagation();toggleDetail('${rowId}','${detailId}')">✕</button>
                    </div>
                    <div class="detail-meta">
                        <div class="detail-meta-item">📅 <span>${escapeHtml(date)}</span></div>
                        <div class="detail-meta-item">📰 <span>${escapeHtml(source)}</span></div>
                        <div class="detail-meta-item">🏷 <span>${escapeHtml(srcType)}</span></div>
                        ${sourceLink}
                    </div>
                    <div class="detail-grid">
                        <div>
                            <div class="detail-section-label">Main Theme</div>
                            <div class="detail-section-content">${mainBadge}</div>
                        </div>
                        <div>
                            <div class="detail-section-label">Secondary Themes</div>
                            <div class="detail-section-content">${allSecBadges}</div>
                        </div>
                        <div>
                            <div class="detail-section-label">Countries</div>
                            <div class="detail-section-content">${allCountryPills}</div>
                        </div>
                        <div>
                            <div class="detail-section-label">Organizations</div>
                            <div class="detail-section-content">${allOrgPills}</div>
                        </div>
                        <div>
                            <div class="detail-section-label">Persons</div>
                            <div class="detail-section-content">${allPersonPills}</div>
                        </div>
                        <div>
                            <div class="detail-section-label">Locations</div>
                            <div class="detail-section-content">${allLocationPills}</div>
                        </div>
                    </div>
                    <div>
                        <div class="detail-section-label" style="margin-bottom:.5rem;">Content</div>
                        <div class="detail-content-text">${contentFull}</div>
                    </div>
                </div>
            </td>
        </tr>`;
    }).join('');

}

// ════════════════════════════════════════
// EXPANDABLE ROWS
// ════════════════════════════════════════

function toggleDetail(rowId, detailId) {
    const row    = document.getElementById(rowId);
    const detail = document.getElementById(detailId);
    if (!row || !detail) return;
    const isOpen = detail.classList.contains('open');
    if (isOpen) {
        detail.classList.remove('open');
        row.classList.remove('expanded');
    } else {
        detail.classList.add('open');
        row.classList.add('expanded');
    }
}

// ════════════════════════════════════════
// HELPERS
// ════════════════════════════════════════

function escapeHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

function buildPreview(content, maxChars) {
    if (!content) return '—';
    const normalized = content.replace(/\s+/g, ' ').trim();
    if (!normalized) return '—';
    if (normalized.length <= maxChars) return normalized;
    const truncated = normalized.slice(0, maxChars).trimEnd();
    const lastSpace = truncated.lastIndexOf(' ');
    return (lastSpace > 0 ? truncated.slice(0, lastSpace) : truncated) + '...';
}

function themeBadgeHtml(themeKey) {
    const cfg   = THEME_BADGES[themeKey] || THEME_BADGES.other_mixed;
    const label = THEME_LABELS[themeKey] || themeKey;
    return `<span class="theme-badge" style="background:${cfg.bg};color:${cfg.text};border-color:${cfg.border};">${escapeHtml(label)}</span>`;
}

function pillsHtml(values, max) {
    if (!values || !values.length) return '<span class="cell-muted">—</span>';
    const visible = values.slice(0, max);
    const hidden  = values.length - max;
    const pills   = visible.map(v => `<span class="entity-pill">${escapeHtml(v)}</span>`).join('');
    const more    = hidden > 0 ? `<span class="entity-more">+${hidden}</span>` : '';
    return `<div class="pills-row">${pills}${more}</div>`;
}

function entityPillsAll(values) {
    if (!values || !values.length) return '<span class="cell-muted">—</span>';
    return values.map(v => `<span class="entity-pill">${escapeHtml(v)}</span>`).join('');
}

// ════════════════════════════════════════
// OVERVIEW — CHARTS
// ════════════════════════════════════════

const chartInstances = {};

const CHART_COLORS = {
    support_ukraine:               '#7EB8FF',
    eastern_flank_nato_deterrence: '#B8A8FF',
    romania_republic_of_moldova:   '#FFB87A',
    russia_regional_implications:  '#FF9494',
    eu_regional_security:          '#5EDBA0',
    black_sea_regional_security:   '#60CCFF',
    other_mixed:                   '#7A9DC0',
};

const CHART_DEFAULTS = {
    color: '#7A9DC0',
    borderColor: '#182A42',
    font: { family: "'IBM Plex Sans', sans-serif" },
};

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

function renderOverview(docs) {
    if (!docs || !docs.length) return;
    configureChartDefaults();
    renderSummaryStrip(docs);
    renderTimelineChart(docs);
    renderSourceChart(docs);
    renderThemeChart(docs);
    renderCountryChart(docs);
    renderOrgChart(docs);
    renderThemeEvolutionChart(docs);
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

    // Group by week (ISO week start = Monday)
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

    // Fill gaps
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

// ── Theme evolution (stacked bar by month) ──
function renderThemeEvolutionChart(docs) {
    const ctx = document.getElementById('chart-theme-evolution');
    if (!ctx) return;
    if (chartInstances.themeEvolution) chartInstances.themeEvolution.destroy();

    // Group by month and theme
    const monthThemeMap = {};
    const allThemeKeys = new Set();
    docs.forEach(d => {
        if (!d.publication_date_iso) return;
        const month = d.publication_date_iso.slice(0, 7); // YYYY-MM
        const theme = d.main_theme || 'other_mixed';
        allThemeKeys.add(theme);
        if (!monthThemeMap[month]) monthThemeMap[month] = {};
        monthThemeMap[month][theme] = (monthThemeMap[month][theme] || 0) + 1;
    });

    const sortedMonths = Object.keys(monthThemeMap).sort();
    const themeKeys = [...allThemeKeys];

    // Fill all months in range
    const allMonths = [];
    if (sortedMonths.length > 1) {
        let [year, month] = sortedMonths[0].split('-').map(Number);
        const [endYear, endMonth] = sortedMonths[sortedMonths.length - 1].split('-').map(Number);
        while (year < endYear || (year === endYear && month <= endMonth)) {
            const key = `${year}-${String(month).padStart(2, '0')}`;
            allMonths.push(key);
            month++;
            if (month > 12) { month = 1; year++; }
        }
    } else {
        allMonths.push(...sortedMonths);
    }

    const datasets = themeKeys.map(tk => ({
        label: THEME_LABELS[tk] || tk,
        data: allMonths.map(m => (monthThemeMap[m] && monthThemeMap[m][tk]) || 0),
        backgroundColor: (CHART_COLORS[tk] || '#7A9DC0') + '66',
        borderColor: CHART_COLORS[tk] || '#7A9DC0',
        borderWidth: 1,
        borderRadius: 3,
    }));

    chartInstances.themeEvolution = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: allMonths.map(m => {
                const [y, mo] = m.split('-');
                const dt = new Date(Number(y), Number(mo) - 1);
                return dt.toLocaleDateString('en-GB', { month: 'short', year: '2-digit' });
            }),
            datasets,
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { usePointStyle: true, pointStyle: 'circle', font: { size: 10 }, padding: 12 }
                },
            },
            scales: {
                x: {
                    stacked: true,
                    grid: { display: false },
                    ticks: { font: { family: "'IBM Plex Mono', monospace", size: 10 } },
                },
                y: {
                    stacked: true,
                    beginAtZero: true,
                    ticks: { stepSize: 1, font: { family: "'IBM Plex Mono', monospace", size: 10 } },
                    grid: { color: 'rgba(24,42,66,.3)' },
                }
            }
        }
    });
    ctx.parentElement.style.height = '280px';
}

// ════════════════════════════════════════
// INIT
// ════════════════════════════════════════

loadDocuments().catch(err => console.error('Failed to load documents:', err));