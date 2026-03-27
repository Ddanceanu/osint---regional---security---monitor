// ════════════════════════════════════════
// DOCUMENT EXPLORER
// Filters, table, KPIs, detail panel
// ════════════════════════════════════════

import { THEME_LABELS } from './constants.js';
import { appState } from './state.js';
import { escapeHtml, buildPreview, themeBadgeHtml, pillsHtml, entityPillsAll } from './utils.js';

// ════════════════════════════════════════
// FILTER INIT
// ════════════════════════════════════════

export function initFilters() {
    const sources      = [...new Set(appState.allDocuments.map(d => d.source_name).filter(Boolean))].sort();
    const themeKeys    = [...new Set(appState.allDocuments.map(d => d.main_theme).filter(Boolean))];
    const allCountries = [...new Set(appState.allDocuments.flatMap(d => d.entities?.countries || []))].sort();
    const allOrgs      = [...new Set(appState.allDocuments.flatMap(d => d.entities?.organizations || []))].sort();

    // Default: sources and themes all selected, countries/orgs none
    sources.forEach(s => appState.sources.add(s));
    themeKeys.forEach(t => appState.themes.add(t));

    // Dates
    const dates = appState.allDocuments.map(d => d.publication_date_iso).filter(Boolean).sort();
    if (dates.length) {
        appState.dateFrom = dates[0];
        appState.dateTo   = new Date().toISOString().slice(0, 10);
        document.getElementById('date-from').value = appState.dateFrom;
        document.getElementById('date-to').value   = appState.dateTo;
    }

    // Build checklists
    buildChecklist('source-list', sources, appState.sources, true);
    buildChecklist('theme-list',  themeKeys, appState.themes, true, k => THEME_LABELS[k] || k);
    buildChecklist('country-list', allCountries, appState.countries, false);
    buildChecklist('org-list',     allOrgs,      appState.organizations, false);

    // Search
    document.getElementById('search-input').addEventListener('input', e => {
        appState.search = e.target.value;
        refresh();
    });

    // Dates
    document.getElementById('date-from').addEventListener('change', e => {
        appState.dateFrom = e.target.value;
        refresh();
    });

    document.getElementById('date-to').addEventListener('change', e => {
        appState.dateTo = e.target.value;
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
    renderTable(appState.filteredDocuments);
    renderKPIs(appState.filteredDocuments);
}

// ════════════════════════════════════════
// RESET FILTERS (exposed globally for onclick)
// ════════════════════════════════════════

export function resetFilters() {
    appState.search = '';
    appState.countries.clear();
    appState.organizations.clear();

    const allSources  = [...new Set(appState.allDocuments.map(d => d.source_name).filter(Boolean))];
    const allThemes   = [...new Set(appState.allDocuments.map(d => d.main_theme).filter(Boolean))];
    appState.sources.clear();
    allSources.forEach(s => appState.sources.add(s));
    appState.themes.clear();
    allThemes.forEach(t => appState.themes.add(t));

    const dates = appState.allDocuments.map(d => d.publication_date_iso).filter(Boolean).sort();
    if (dates.length) {
        appState.dateFrom = dates[0];
        appState.dateTo   = new Date().toISOString().slice(0, 10);
    }

    document.getElementById('search-input').value = '';
    document.getElementById('date-from').value    = appState.dateFrom;
    document.getElementById('date-to').value      = appState.dateTo;

    buildChecklist('source-list',  [...new Set(appState.allDocuments.map(d => d.source_name).filter(Boolean))].sort(), appState.sources, true);
    buildChecklist('theme-list',   [...new Set(appState.allDocuments.map(d => d.main_theme).filter(Boolean))], appState.themes, true, k => THEME_LABELS[k] || k);
    buildChecklist('country-list', [...new Set(appState.allDocuments.flatMap(d => d.entities?.countries || []))].sort(), appState.countries, false);
    buildChecklist('org-list',     [...new Set(appState.allDocuments.flatMap(d => d.entities?.organizations || []))].sort(), appState.organizations, false);

    refresh();
}

// ════════════════════════════════════════
// APPLY FILTERS
// ════════════════════════════════════════

export function applyFilters() {
    appState.filteredDocuments = appState.allDocuments.filter(doc => {
        if (appState.search.trim()) {
            const term = appState.search.trim().toLowerCase();
            const inTitle   = (doc.title || '').toLowerCase().includes(term);
            const inContent = (doc.content || '').toLowerCase().includes(term);
            if (!inTitle && !inContent) return false;
        }

        if (appState.sources.size > 0 && !appState.sources.has(doc.source_name)) return false;
        if (appState.themes.size > 0  && !appState.themes.has(doc.main_theme))   return false;

        if (appState.dateFrom && doc.publication_date_iso && doc.publication_date_iso < appState.dateFrom) return false;
        if (appState.dateTo   && doc.publication_date_iso && doc.publication_date_iso > appState.dateTo)   return false;

        if (appState.countries.size > 0) {
            const docCountries = doc.entities?.countries || [];
            if (![...appState.countries].some(c => docCountries.includes(c))) return false;
        }

        if (appState.organizations.size > 0) {
            const docOrgs = doc.entities?.organizations || [];
            if (![...appState.organizations].some(o => docOrgs.includes(o))) return false;
        }

        return true;
    });
}

// ════════════════════════════════════════
// KPI CARDS
// ════════════════════════════════════════

export function renderKPIs(docs) {
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

export function renderDatasetStrip() {
    const dates = appState.allDocuments.map(d => d.publication_date_iso).filter(Boolean).sort();
    const dateRange = dates.length ? `${dates[0]} → ${dates[dates.length - 1]}` : 'N/A';

    const strip = document.getElementById('dataset-strip');
    if (!strip) return;

    strip.innerHTML = `
        <div class="ds-item"><span>Documents</span><span class="ds-val">${appState.allDocuments.length}</span></div>
        <div class="ds-sep"></div>
        <div class="ds-item"><span>Date range</span><span class="ds-val">${dateRange}</span></div>
        <div class="ds-sep"></div>
        <div class="ds-item"><span>Source</span><span class="ds-val">documents.json</span></div>
    `;
}

// ════════════════════════════════════════
// TABLE RENDER
// ════════════════════════════════════════

export function renderTable(docs) {
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
// EXPANDABLE ROWS (exposed globally for onclick)
// ════════════════════════════════════════

export function toggleDetail(rowId, detailId) {
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
