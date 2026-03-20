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
// INIT
// ════════════════════════════════════════

loadDocuments().catch(err => console.error('Failed to load documents:', err));