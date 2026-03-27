// ════════════════════════════════════════
// SOURCE DIVERGENCE
// Split Intelligence View — butterfly charts
// ════════════════════════════════════════

import { THEME_LABELS } from './constants.js';

console.log('[SD] Source divergence module v2 loaded');
let cachedData = null;
let activeEntityTab = 'countries';

const MAX_ENTITIES = 5;

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
// BUTTERFLY ROW BUILDER
// ════════════════════════════════════════

function buildButterflyRow(name, offShare, ttShare, maxShare) {
    const offWidth = maxShare > 0 ? (offShare / maxShare) * 100 : 0;
    const ttWidth = maxShare > 0 ? (ttShare / maxShare) * 100 : 0;

    const gap = +(ttShare - offShare).toFixed(1);
    const absGap = Math.abs(gap);
    let gapClass, gapText;

    if (gap > 0) {
        gapClass = 'gap-thinktank';
        gapText = `+${absGap}pp`;
    } else if (gap < 0) {
        gapClass = 'gap-official';
        gapText = `+${absGap}pp`;
    } else {
        gapClass = 'gap-neutral';
        gapText = `0pp`;
    }

    return `
        <div class="sd-butterfly-row">
            <div class="sd-butterfly-left">
                <span class="sd-bar-label">${offShare > 0 ? offShare + '%' : ''}</span>
                <div class="sd-bar-track">
                    <div class="sd-bar-fill" style="width: ${offWidth}%"></div>
                </div>
            </div>
            <div class="sd-butterfly-center">
                <span class="sd-butterfly-name">${name}</span>
                <span class="sd-gap-badge ${gapClass}">${gapText}</span>
            </div>
            <div class="sd-butterfly-right">
                <div class="sd-bar-track">
                    <div class="sd-bar-fill" style="width: ${ttWidth}%"></div>
                </div>
                <span class="sd-bar-label">${ttShare > 0 ? ttShare + '%' : ''}</span>
            </div>
        </div>
    `;
}

// ════════════════════════════════════════
// THEME BUTTERFLY
// ════════════════════════════════════════

function renderThemeButterfly(data) {
    const container = document.getElementById('sd-butterfly-themes');
    if (!container) return;

    const gaps = data.divergence.theme_gaps;

    // Sort by max share for readable layout
    const sorted = [...gaps].sort((a, b) => {
        const maxA = Math.max(a.official_share, a.think_tank_share);
        const maxB = Math.max(b.official_share, b.think_tank_share);
        return maxB - maxA;
    });

    const maxShare = Math.max(...sorted.map(g => Math.max(g.official_share, g.think_tank_share)), 1);

    container.innerHTML = sorted.map(g => {
        const displayName = THEME_LABELS[g.theme] || g.theme;
        return buildButterflyRow(displayName, g.official_share, g.think_tank_share, maxShare);
    }).join('');
}

// ════════════════════════════════════════
// ENTITY BUTTERFLY
// ════════════════════════════════════════

function renderEntityButterfly(data, category) {
    const container = document.getElementById('sd-butterfly-entities');
    if (!container) return;

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

    const maxShare = Math.max(...top.map(e => Math.max(e.official, e.thinkTank)), 1);

    container.innerHTML = top.map(e =>
        buildButterflyRow(e.name, e.official, e.thinkTank, maxShare)
    ).join('');
}

// ════════════════════════════════════════
// UPDATE HEADER INFO
// ════════════════════════════════════════

function updateHeader(data) {
    // Period
    const periodEl = document.getElementById('sd-period');
    if (periodEl && data.period_start && data.period_end) {
        periodEl.textContent = `Analysis period: ${data.period_start} → ${data.period_end}  ·  ${data.total_documents} documents`;
    }

    // Official meta
    const offMeta = document.getElementById('sd-meta-official');
    if (offMeta) {
        offMeta.textContent = `${data.official.num_sources} sources · ${data.official.total_documents} docs`;
    }

    // Think tank meta
    const ttMeta = document.getElementById('sd-meta-thinktank');
    if (ttMeta) {
        ttMeta.textContent = `${data.think_tank.num_sources} sources · ${data.think_tank.total_documents} docs`;
    }
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
            if (data) renderEntityButterfly(data, activeEntityTab);
        });
    });
}

// ════════════════════════════════════════
// MAIN RENDER
// ════════════════════════════════════════

export async function renderSourceDivergence() {
    console.log('[SD] renderSourceDivergence called');
    const data = await loadDivergenceData();
    if (!data) { console.log('[SD] no data'); return; }
    console.log('[SD] data loaded, themes:', data.divergence?.theme_gaps?.length);

    updateHeader(data);
    renderThemeButterfly(data);
    renderEntityButterfly(data, activeEntityTab);
    console.log('[SD] render complete');
}
