// ════════════════════════════════════════
// SHARED APPLICATION STATE
// ════════════════════════════════════════

export const appState = {
    allDocuments:      [],
    filteredDocuments: [],
    search:            "",
    sources:           new Set(),
    themes:            new Set(),
    countries:         new Set(),
    organizations:     new Set(),
    dateFrom:          "",
    dateTo:            "",
};

// Chart.js instance registry (for destroy-before-recreate)
export const chartInstances = {};
export const trendingChartInstances = {};
