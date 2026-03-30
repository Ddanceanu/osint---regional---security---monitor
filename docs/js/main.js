// ════════════════════════════════════════
// MAIN — Application entry point
// ════════════════════════════════════════

import { appState } from './state.js';
import { initNavigation, updateTimestamp } from './navigation.js';
import { initFilters, applyFilters, renderTable, renderKPIs, renderDatasetStrip, resetFilters, toggleDetail } from './explorer.js';
import { renderOverview } from './overview.js';
import { renderTrending } from './strategic-pulse.js';
import { renderThemeEvolutionChart, initThemeShiftToggle } from './theme-shift.js';
import { renderSourceDivergence, initDivergenceTabs } from './source-divergence.js';
import { renderActorTrajectories } from './actor-trajectories.js';
import { renderThemesPage } from './themes.js';

// ════════════════════════════════════════
// EXPOSE GLOBALS (needed for onclick handlers in HTML)
// ════════════════════════════════════════

window.toggleDetail = toggleDetail;
window.resetFilters = resetFilters;

// ════════════════════════════════════════
// INIT
// ════════════════════════════════════════

initNavigation();
updateTimestamp();
initThemeShiftToggle();
initDivergenceTabs();

// ════════════════════════════════════════
// LOAD DOCUMENTS
// ════════════════════════════════════════

async function loadDocuments() {
    try {
        console.log('Fetching documents...');
        const response = await fetch('data/documents.json');
        appState.allDocuments = await response.json();
        console.log('Documents loaded:', appState.allDocuments.length);

        initFilters();
        applyFilters();
        renderTable(appState.filteredDocuments);
        renderKPIs(appState.filteredDocuments);
        renderDatasetStrip();
        renderOverview(appState.allDocuments);
        renderTrending();
        renderThemeEvolutionChart();
        renderSourceDivergence();
        renderActorTrajectories();
        renderThemesPage();

    } catch (error) {
        console.error('Failed to load documents:', error);
        document.getElementById('table-body').innerHTML =
            '<tr><td colspan="8" class="table-loading">Failed to load documents. Make sure the server is running.</td></tr>';
    }
}

loadDocuments();
