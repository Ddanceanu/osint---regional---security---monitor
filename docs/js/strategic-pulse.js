// ════════════════════════════════════════
// STRATEGIC PULSE
// Trending panel, momentum board, sparklines
// ════════════════════════════════════════

import { THEME_LABELS, ENTITY_IMAGES, CATEGORY_LABELS } from './constants.js';
import { trendingChartInstances } from './state.js';

// ════════════════════════════════════════
// RENDER TRENDING (entry point)
// ════════════════════════════════════════

export function renderTrending() {
    fetch('data/trending.json')
        .then(res => res.json())
        .then(data => {
            // Update period label
            const periodEl = document.getElementById('trending-period');
            if (periodEl) {
                const currStart = new Date(data.period_start + 'T00:00:00');
                const prevStart = new Date(currStart);
                prevStart.setDate(prevStart.getDate() - data.period_days);
                const prevStartStr = prevStart.toISOString().slice(0, 10);
                periodEl.textContent = `${prevStartStr} → ${data.period_end}  ·  28 days  ·  ${data.total_documents_in_period} docs (current 14d)`;
            }

            // Render each category
            renderTrendingCategory('trending-persons', data.categories.persons);
            renderTrendingCategory('trending-countries', data.categories.countries);
            renderTrendingCategory('trending-organizations', data.categories.organizations);
            renderTrendingCategory('trending-themes', data.categories.themes, true);

            // Draw line charts for each category
            drawTrendingChart('chart-trending-persons', data.categories.persons, data.period_days, data.period_start);
            drawTrendingChart('chart-trending-countries', data.categories.countries, data.period_days, data.period_start);
            drawTrendingChart('chart-trending-organizations', data.categories.organizations, data.period_days, data.period_start);
            drawTrendingChart('chart-trending-themes', data.categories.themes, data.period_days, data.period_start, true);

            // Render momentum board
            if (data.momentum_board) {
                renderMomentumBoard(data.momentum_board);
            }
        })
        .catch(err => console.error('Failed to load trending data:', err));
}

// ════════════════════════════════════════
// CATEGORY RENDERING
// ════════════════════════════════════════

function renderTrendingCategory(containerId, categoryData, isTheme = false) {
    const container = document.getElementById(containerId);
    if (!container || !categoryData || !categoryData.top) return;

    const topEl = container.querySelector('.trending-top');
    const runnersEl = container.querySelector('.trending-runners');

    // Render top item
    const top = categoryData.top;
    const topDisplayName = isTheme ? (THEME_LABELS[top.name] || top.name) : top.name;

    topEl.innerHTML = `
        <div class="trending-top-item">
            ${buildAvatar(top.name, topDisplayName, false)}
            <div class="trending-top-info">
                <div class="trending-top-name">${topDisplayName}</div>
                <div class="trending-top-stats">
                    <span class="trending-pct">${top.percentage}% visibility</span>
                </div>
            </div>
            <div class="trending-right">
                ${buildTrendBadge(top.trend)}
                <canvas class="trending-spark" id="spark-${containerId}-top"></canvas>
            </div>
        </div>
    `;

    drawSparkline(`spark-${containerId}-top`, top.sparkline);

    // Render runners-up
    runnersEl.innerHTML = '';
    (categoryData.runners_up || []).forEach((runner, idx) => {
        const runnerDisplayName = isTheme ? (THEME_LABELS[runner.name] || runner.name) : runner.name;

        const div = document.createElement('div');
        div.className = 'trending-runner-item';
        div.innerHTML = `
            ${buildAvatar(runner.name, runnerDisplayName, true)}
            <div class="trending-runner-info">
                <div class="trending-runner-name">${runnerDisplayName}</div>
                <div class="trending-runner-stats">
                    <span class="trending-runner-pct">${runner.percentage}% visibility</span>
                </div>
            </div>
            <div class="trending-right-small">
                ${buildTrendBadge(runner.trend)}
                <canvas class="trending-runner-spark" id="spark-${containerId}-r${idx}"></canvas>
            </div>
        `;
        runnersEl.appendChild(div);

        drawSparkline(`spark-${containerId}-r${idx}`, runner.sparkline);
    });
}

// ════════════════════════════════════════
// MOMENTUM BOARD
// ════════════════════════════════════════

function renderMomentumBoard(board) {
    const risersEl = document.getElementById('momentum-risers-list');
    const fallersEl = document.getElementById('momentum-fallers-list');
    if (!risersEl || !fallersEl) return;

    const maxSources = 7;

    function buildMomentumItem(entry, rank, type) {
        const catLabel = CATEGORY_LABELS[entry.category] || entry.category;
        const changeClass = type === 'rise' ? 'rise' : 'fall';
        const displayName = entry.category === 'themes'
            ? (THEME_LABELS[entry.name] || entry.name)
            : entry.name;

        let dotsHtml = '';
        for (let i = 0; i < maxSources; i++) {
            dotsHtml += `<div class="momentum-source-dot ${i < entry.source_diversity ? '' : 'inactive'}"></div>`;
        }

        const prevRate = entry.previous_rate != null ? entry.previous_rate : '?';
        const currRate = entry.current_rate != null ? entry.current_rate : '?';
        const rateShift = `${prevRate}% → ${currRate}%`;
        const momentumDisplay = entry.momentum_score.toFixed(1);

        return `
            <div class="momentum-item">
                <span class="momentum-rank">${rank}.</span>
                <span class="momentum-item-name">${displayName}</span>
                <span class="momentum-item-category">${catLabel}</span>
                <span class="momentum-rate-shift" title="Presence rate: previous → current period">${rateShift}</span>
                <span class="momentum-score-badge ${changeClass}" title="Momentum score (rate × direction)">${momentumDisplay}</span>
                <div class="momentum-sources" title="${entry.source_diversity} of ${maxSources} sources">${dotsHtml}</div>
            </div>
        `;
    }

    const columnHeaders = `
        <div class="momentum-col-headers">
            <span class="mch-rank">#</span>
            <span class="mch-name">ENTITY</span>
            <span class="mch-cat">TYPE</span>
            <span class="mch-rate">PRESENCE</span>
            <span class="mch-score">SCORE</span>
            <span class="mch-sources">SOURCES</span>
        </div>
    `;

    if (board.risers && board.risers.length > 0) {
        risersEl.innerHTML = columnHeaders + board.risers.map((e, i) => buildMomentumItem(e, i + 1, 'rise')).join('');
    } else {
        risersEl.innerHTML = columnHeaders + '<div class="momentum-empty">No significant risers in this period</div>';
    }

    if (board.fallers && board.fallers.length > 0) {
        fallersEl.innerHTML = columnHeaders + board.fallers.map((e, i) => buildMomentumItem(e, i + 1, 'fall')).join('');
    } else {
        fallersEl.innerHTML = columnHeaders + '<div class="momentum-empty">No significant fallers in this period</div>';
    }
}

// ════════════════════════════════════════
// HELPERS
// ════════════════════════════════════════

function buildTrendBadge(trend) {
    if (!trend) return '';

    const dir = trend.direction;
    let arrow, cls;

    if (dir === 'up') {
        arrow = '▲';
        cls = 'trend-up';
    } else if (dir === 'down') {
        arrow = '▼';
        cls = 'trend-down';
    } else {
        arrow = '—';
        cls = 'trend-stable';
    }

    const pct = Math.abs(trend.change_pct);
    let pctLabel;
    if (pct > 200) {
        const sign = trend.change_pct >= 0 ? '+' : '-';
        pctLabel = `${sign}>200%`;
    } else {
        const sign = trend.change_pct >= 0 ? '+' : '';
        pctLabel = `${sign}${trend.change_pct}%`;
    }

    return `<div class="trend-badge ${cls}">
        <span class="trend-arrow">${arrow}</span>
        <span class="trend-pct-value">${pctLabel}</span>
        <span class="trend-context">vs prev 14d</span>
    </div>`;
}

function buildAvatar(entityName, displayName, isSmall) {
    const imgPath = ENTITY_IMAGES[entityName];

    if (imgPath) {
        const cls = isSmall ? 'trending-runner-avatar' : 'trending-avatar';
        return `<img class="${cls}" src="${imgPath}" alt="${displayName}">`;
    }

    const cls = isSmall ? 'trending-runner-placeholder' : 'trending-avatar-placeholder';
    const letter = displayName.charAt(0).toUpperCase();
    return `<div class="${cls}">${letter}</div>`;
}

function drawSparkline(canvasId, data) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !data || !data.length) return;

    const ctx = canvas.getContext('2d');
    const w = canvas.width = canvas.offsetWidth * 2;
    const h = canvas.height = canvas.offsetHeight * 2;
    ctx.scale(2, 2);

    const drawW = canvas.offsetWidth;
    const drawH = canvas.offsetHeight;

    const max = Math.max(...data, 1);
    const step = drawW / (data.length - 1 || 1);

    ctx.beginPath();
    ctx.strokeStyle = '#00CFFF';
    ctx.lineWidth = 1.5;
    ctx.lineJoin = 'round';

    data.forEach((val, i) => {
        const x = i * step;
        const y = drawH - (val / max) * (drawH - 4) - 2;
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    });
    ctx.stroke();

    ctx.lineTo((data.length - 1) * step, drawH);
    ctx.lineTo(0, drawH);
    ctx.closePath();
    const gradient = ctx.createLinearGradient(0, 0, 0, drawH);
    gradient.addColorStop(0, 'rgba(0, 207, 255, 0.15)');
    gradient.addColorStop(1, 'rgba(0, 207, 255, 0)');
    ctx.fillStyle = gradient;
    ctx.fill();
}

// ════════════════════════════════════════
// TRENDING LINE CHARTS
// ════════════════════════════════════════

function drawTrendingChart(canvasId, categoryData, periodDays, periodStart, isTheme = false) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !categoryData || !categoryData.top) return;

    if (trendingChartInstances[canvasId]) {
        trendingChartInstances[canvasId].destroy();
    }

    const totalDays = periodDays * 2;

    const labels = [];
    const currentStart = new Date(periodStart + 'T00:00:00');
    const fullStart = new Date(currentStart);
    fullStart.setDate(fullStart.getDate() - periodDays);
    for (let i = 0; i < totalDays; i++) {
        const d = new Date(fullStart);
        d.setDate(d.getDate() + i);
        const month = d.toLocaleString('en', { month: 'short' });
        labels.push(`${month} ${d.getDate()}`);
    }

    const top = categoryData.top;
    const topName = isTheme ? (THEME_LABELS[top.name] || top.name) : top.name;
    const datasets = [
        {
            label: topName,
            data: top.sparkline,
            borderColor: '#00CFFF',
            backgroundColor: 'rgba(0, 207, 255, 0.08)',
            borderWidth: 2,
            fill: true,
            tension: 0.3,
            pointRadius: 2,
            pointBackgroundColor: '#00CFFF'
        }
    ];

    const runnerColors = ['#a78bfa', '#f59e0b'];
    (categoryData.runners_up || []).forEach((runner, idx) => {
        const runnerName = isTheme ? (THEME_LABELS[runner.name] || runner.name) : runner.name;
        datasets.push({
            label: runnerName,
            data: runner.sparkline,
            borderColor: runnerColors[idx] || '#94a3b8',
            backgroundColor: 'transparent',
            borderWidth: 1.5,
            borderDash: [4, 3],
            fill: false,
            tension: 0.3,
            pointRadius: 1.5,
            pointBackgroundColor: runnerColors[idx] || '#94a3b8'
        });
    });

    const periodSeparator = {
        id: 'periodSeparator',
        afterDraw(chart) {
            const xScale = chart.scales.x;
            const yScale = chart.scales.y;
            const separatorIndex = periodDays;
            if (separatorIndex >= xScale.ticks.length) return;

            const xPos = xScale.getPixelForValue(separatorIndex);
            const ctx = chart.ctx;

            ctx.save();
            ctx.beginPath();
            ctx.setLineDash([4, 4]);
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.25)';
            ctx.lineWidth = 1;
            ctx.moveTo(xPos, yScale.top);
            ctx.lineTo(xPos, yScale.bottom);
            ctx.stroke();

            ctx.setLineDash([]);
            ctx.font = "8px 'JetBrains Mono', monospace";
            ctx.textAlign = 'center';
            ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';

            const prevCenter = (xScale.getPixelForValue(0) + xPos) / 2;
            const currCenter = (xPos + xScale.getPixelForValue(totalDays - 1)) / 2;
            ctx.fillText('prev 14d', prevCenter, yScale.top + 12);
            ctx.fillText('current 14d', currCenter, yScale.top + 12);
            ctx.restore();
        }
    };

    trendingChartInstances[canvasId] = new Chart(canvas, {
        type: 'line',
        data: { labels, datasets },
        plugins: [periodSeparator],
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        color: '#8892a4',
                        font: { size: 9, family: "'JetBrains Mono', monospace" },
                        boxWidth: 12,
                        padding: 8,
                        usePointStyle: true,
                        pointStyle: 'line'
                    }
                },
                tooltip: {
                    backgroundColor: '#0d1b2a',
                    borderColor: '#1e3a5f',
                    borderWidth: 1,
                    titleFont: { size: 10 },
                    bodyFont: { size: 10 },
                    callbacks: {
                        label: ctx => `${ctx.dataset.label}: ${ctx.parsed.y}%`
                    }
                }
            },
            scales: {
                x: {
                    ticks: {
                        color: '#5a6577',
                        font: { size: 8, family: "'JetBrains Mono', monospace" },
                        maxRotation: 45,
                        maxTicksLimit: 10
                    },
                    grid: { color: 'rgba(30, 58, 95, 0.3)', drawBorder: false }
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#5a6577',
                        font: { size: 8, family: "'JetBrains Mono', monospace" },
                        callback: value => value + '%'
                    },
                    grid: { color: 'rgba(30, 58, 95, 0.3)', drawBorder: false }
                }
            }
        }
    });
}
