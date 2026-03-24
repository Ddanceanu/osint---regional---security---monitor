// ════════════════════════════════════════
// SHARED UTILITIES
// ════════════════════════════════════════

import { THEME_LABELS, THEME_BADGES } from './constants.js';

export function escapeHtml(str) {
    return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

export function buildPreview(content, maxChars) {
    if (!content) return '—';
    const normalized = content.replace(/\s+/g, ' ').trim();
    if (!normalized) return '—';
    if (normalized.length <= maxChars) return normalized;
    const truncated = normalized.slice(0, maxChars).trimEnd();
    const lastSpace = truncated.lastIndexOf(' ');
    return (lastSpace > 0 ? truncated.slice(0, lastSpace) : truncated) + '...';
}

export function themeBadgeHtml(themeKey) {
    const cfg   = THEME_BADGES[themeKey] || THEME_BADGES.other_mixed;
    const label = THEME_LABELS[themeKey] || themeKey;
    return `<span class="theme-badge" style="background:${cfg.bg};color:${cfg.text};border-color:${cfg.border};">${escapeHtml(label)}</span>`;
}

export function pillsHtml(values, max) {
    if (!values || !values.length) return '<span class="cell-muted">—</span>';
    const visible = values.slice(0, max);
    const hidden  = values.length - max;
    const pills   = visible.map(v => `<span class="entity-pill">${escapeHtml(v)}</span>`).join('');
    const more    = hidden > 0 ? `<span class="entity-more">+${hidden}</span>` : '';
    return `<div class="pills-row">${pills}${more}</div>`;
}

export function entityPillsAll(values) {
    if (!values || !values.length) return '<span class="cell-muted">—</span>';
    return values.map(v => `<span class="entity-pill">${escapeHtml(v)}</span>`).join('');
}
