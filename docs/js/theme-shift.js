// ════════════════════════════════════════
// THEMATIC SHIFT
// Stacked bar chart + Share/Absolute toggle
// ════════════════════════════════════════

import { THEME_LABELS, THEME_SHIFT_COLORS } from './constants.js';
import { chartInstances } from './state.js';

let themeShiftMode = 'share'; // 'share' or 'absolute'

// ════════════════════════════════════════
// RENDER CHART
// ════════════════════════════════════════

export async function renderThemeEvolutionChart() {
    const ctx = document.getElementById('chart-theme-evolution');
    if (!ctx) return;
    if (chartInstances.themeEvolution) chartInstances.themeEvolution.destroy();

    let data;
    try {
        const res = await fetch('data/theme_shift.json');
        data = await res.json();
    } catch (e) {
        console.error('Failed to load theme_shift.json:', e);
        return;
    }

    const MIN_DOCS = 5;
    const weeks = data.weeks.filter(w => w.total >= MIN_DOCS);
    if (!weeks.length) return;

    const themes = data.themes;
    const isShare = themeShiftMode === 'share';

    const datasets = themes.map(tk => ({
        label: THEME_LABELS[tk] || tk,
        data: weeks.map(w => isShare ? w.shares[tk] : w.counts[tk]),
        backgroundColor: THEME_SHIFT_COLORS[tk] || '#5C6B7E',
        borderColor: 'rgba(6,12,22,0.6)',
        borderWidth: 0.5,
        borderSkipped: false,
    }));

    chartInstances.themeEvolution = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: weeks.map(w => {
                const [yw, wn] = w.week.split('-W');
                const jan4 = new Date(Number(yw), 0, 4);
                const weekStart = new Date(jan4.getTime() + (Number(wn) - 1) * 7 * 86400000);
                weekStart.setDate(weekStart.getDate() - ((weekStart.getDay() + 6) % 7));
                return weekStart.toLocaleDateString('en-GB', { day: 'numeric', month: 'short' });
            }),
            datasets,
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        usePointStyle: true,
                        pointStyle: 'rectRounded',
                        font: { family: "'IBM Plex Mono', monospace", size: 9.5, weight: '500' },
                        color: '#7A9DC0',
                        padding: 14,
                        boxWidth: 10,
                        boxHeight: 10,
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(8,17,30,0.95)',
                    borderColor: 'rgba(59,123,255,0.2)',
                    borderWidth: 1,
                    titleFont: { family: "'IBM Plex Mono', monospace", size: 10.5, weight: '600' },
                    bodyFont: { family: "'IBM Plex Mono', monospace", size: 10 },
                    padding: 10,
                    callbacks: {
                        label: item => {
                            const w = weeks[item.dataIndex];
                            const tk = themes[item.datasetIndex];
                            const count = w.counts[tk];
                            const share = w.shares[tk];
                            return ` ${item.dataset.label}:  ${count} docs  (${share}%)`;
                        },
                        afterBody: items => {
                            if (!items.length) return '';
                            return `\n  Total: ${weeks[items[0].dataIndex].total} documents`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    stacked: true,
                    grid: { display: false },
                    ticks: {
                        font: { family: "'IBM Plex Mono', monospace", size: 9.5 },
                        color: '#3E5570',
                        maxRotation: 45,
                    },
                    border: { color: 'rgba(24,42,66,.4)' },
                },
                y: {
                    stacked: true,
                    beginAtZero: true,
                    max: isShare ? 100 : undefined,
                    ticks: {
                        font: { family: "'IBM Plex Mono', monospace", size: 9.5 },
                        color: '#3E5570',
                        callback: v => isShare ? v + '%' : v,
                    },
                    grid: { color: 'rgba(24,42,66,.2)', lineWidth: 0.5 },
                    border: { display: false },
                }
            }
        }
    });
}

// ════════════════════════════════════════
// TOGGLE INIT
// ════════════════════════════════════════

export function initThemeShiftToggle() {
    const toggleWrap = document.getElementById('theme-shift-toggle');
    if (!toggleWrap) return;
    toggleWrap.querySelectorAll('.ts-toggle-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            toggleWrap.querySelectorAll('.ts-toggle-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            themeShiftMode = btn.dataset.mode;
            renderThemeEvolutionChart();
        });
    });
}
