// ════════════════════════════════════════
// NAVIGATION & TIMESTAMP
// ════════════════════════════════════════

const pageSubtitles = {
    explorer: 'Document Explorer — analysis workspace',
    overview: 'Corpus summary and analytical context',
    themes:   'Thematic breakdown and trend analysis',
    entities: 'Actors, locations and organizations across the corpus'
};

export function initNavigation() {
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
}

export function updateTimestamp() {
    const now = new Date();
    const formatted = now.toISOString().slice(0, 16).replace('T', ' ') + ' UTC';
    const ts = document.getElementById('explorer-timestamp');
    if (ts) ts.textContent = formatted;
}
