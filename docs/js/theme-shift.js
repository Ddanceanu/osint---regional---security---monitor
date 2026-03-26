// ════════════════════════════════════════
// THEMATIC SHIFT
// Stacked bar chart + theme trend lines
// ════════════════════════════════════════

import { THEME_LABELS, THEME_SHIFT_COLORS } from './constants.js';
import { chartInstances } from './state.js';

let themeShiftMode = 'share'; // 'share' or 'absolute'

// ════════════════════════════════════════
// SHARED: Parse ISO week to start/end dates
// ════════════════════════════════════════

function parseWeekDates(weekStr) {
    const [yw, wn] = weekStr.split('-W');
    const jan4 = new Date(Number(yw), 0, 4);
    const weekStart = new Date(jan4.getTime() + (Number(wn) - 1) * 7 * 86400000);
    weekStart.setDate(weekStart.getDate() - ((weekStart.getDay() + 6) % 7));
    const weekEnd = new Date(weekStart);
    weekEnd.setDate(weekEnd.getDate() + 6);
    return { weekStart, weekEnd, weekNum: wn };
}

function formatWeekLabel(weekStr) {
    const { weekStart, weekEnd } = parseWeekDates(weekStr);
    const startDay = weekStart.getDate();
    const endDay = weekEnd.getDate();
    const startMon = weekStart.toLocaleDateString('en-GB', { month: 'short' });
    const endMon = weekEnd.toLocaleDateString('en-GB', { month: 'short' });

    // Same month: "4–10 Aug"  |  Cross-month: "28 Jan–3 Feb"
    if (startMon === endMon) {
        return `${startDay}–${endDay} ${startMon}`;
    }
    return `${startDay} ${startMon}–${endDay} ${endMon}`;
}

// ════════════════════════════════════════
// SHARED: Load & filter data
// ════════════════════════════════════════

let cachedData = null;

async function loadThemeShiftData() {
    if (cachedData) return cachedData;
    try {
        const res = await fetch('data/theme_shift.json');
        cachedData = await res.json();
        return cachedData;
    } catch (e) {
        console.error('Failed to load theme_shift.json:', e);
        return null;
    }
}

// ════════════════════════════════════════
// STACKED BAR CHART (distribution)
// ════════════════════════════════════════

export async function renderThemeEvolutionChart() {
    const ctx = document.getElementById('chart-theme-evolution');
    if (!ctx) return;
    if (chartInstances.themeEvolution) chartInstances.themeEvolution.destroy();

    const data = await loadThemeShiftData();
    if (!data) return;

    const MIN_DOCS = 5;
    const weeks = data.weeks.filter(w => w.total >= MIN_DOCS);
    if (!weeks.length) return;

    const themes = data.themes;
    const isShare = themeShiftMode === 'share';

    const labels = weeks.map(w => formatWeekLabel(w.week));

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
        data: { labels, datasets },
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
                        title: items => {
                            if (!items.length) return '';
                            const w = weeks[items[0].dataIndex];
                            return `Week: ${formatWeekLabel(w.week)}`;
                        },
                        label: item => {
                            const w = weeks[item.dataIndex];
                            const tk = themes[item.datasetIndex];
                            if (isShare) {
                                return ` ${item.dataset.label}:  ${w.shares[tk]}%`;
                            }
                            return ` ${item.dataset.label}:  ${w.counts[tk]} docs`;
                        },
                        afterBody: items => {
                            if (!items.length) return '';
                            const w = weeks[items[0].dataIndex];
                            return `\n  ${w.num_sources} sources · ${w.total} total docs`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    stacked: true,
                    grid: { display: false },
                    ticks: {
                        font: { family: "'IBM Plex Mono', monospace", size: 8.5 },
                        color: '#3E5570',
                        maxRotation: 50,
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

    // Also render the trend lines chart
    renderThemeTrendsChart(weeks, themes);
}

// ════════════════════════════════════════
// LINE CHART (individual theme trajectories)
// ════════════════════════════════════════

function renderThemeTrendsChart(weeks, themes) {
    const ctx = document.getElementById('chart-theme-trends');
    if (!ctx) return;
    if (chartInstances.themeTrends) chartInstances.themeTrends.destroy();

    const isShare = themeShiftMode === 'share';
    const labels = weeks.map(w => formatWeekLabel(w.week));

    const datasets = themes.map(tk => ({
        label: THEME_LABELS[tk] || tk,
        data: weeks.map(w => isShare ? w.shares[tk] : w.counts[tk]),
        borderColor: THEME_SHIFT_COLORS[tk] || '#5C6B7E',
        backgroundColor: 'transparent',
        borderWidth: 2,
        pointRadius: 3,
        pointBackgroundColor: THEME_SHIFT_COLORS[tk] || '#5C6B7E',
        pointBorderColor: 'rgba(6,12,22,0.4)',
        pointBorderWidth: 1,
        pointHoverRadius: 5,
        tension: 0.25,
        fill: false,
    }));

    chartInstances.themeTrends = new Chart(ctx, {
        type: 'line',
        data: { labels, datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: { display: false },
                tooltip: {
                    backgroundColor: 'rgba(8,17,30,0.95)',
                    borderColor: 'rgba(59,123,255,0.2)',
                    borderWidth: 1,
                    titleFont: { family: "'IBM Plex Mono', monospace", size: 10.5, weight: '600' },
                    bodyFont: { family: "'IBM Plex Mono', monospace", size: 10 },
                    padding: 10,
                    callbacks: {
                        title: items => {
                            if (!items.length) return '';
                            const w = weeks[items[0].dataIndex];
                            return `Week: ${formatWeekLabel(w.week)}`;
                        },
                        label: item => {
                            const w = weeks[item.dataIndex];
                            const tk = themes[item.datasetIndex];
                            if (isShare) {
                                return ` ${item.dataset.label}:  ${w.shares[tk]}%`;
                            }
                            return ` ${item.dataset.label}:  ${w.counts[tk]} docs`;
                        },
                        afterBody: items => {
                            if (!items.length) return '';
                            const w = weeks[items[0].dataIndex];
                            return `\n  ${w.num_sources} sources · ${w.total} total docs`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: {
                        font: { family: "'IBM Plex Mono', monospace", size: 8.5 },
                        color: '#3E5570',
                        maxRotation: 50,
                    },
                    border: { color: 'rgba(24,42,66,.4)' },
                },
                y: {
                    beginAtZero: true,
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
