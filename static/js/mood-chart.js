/**
 * MindCare - Mood Chart JavaScript
 * Handles mood visualization and chart interactions
 */

/**
 * Default chart configuration for mood charts
 */
const MOOD_CHART_CONFIG = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
        intersect: false,
        mode: 'index'
    },
    plugins: {
        legend: {
            display: false
        },
        tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.8)',
            titleColor: 'white',
            bodyColor: 'white',
            borderColor: 'rgba(255, 255, 255, 0.2)',
            borderWidth: 1,
            cornerRadius: 6,
            displayColors: false,
            callbacks: {
                title: function(context) {
                    return `Date: ${context[0].label}`;
                },
                label: function(context) {
                    const score = context.parsed.y;
                    const moodLabels = {
                        1: 'Very Low',
                        2: 'Low', 
                        3: 'Neutral',
                        4: 'Good',
                        5: 'Excellent'
                    };
                    return `Mood: ${score}/5 (${moodLabels[Math.round(score)] || 'Unknown'})`;
                }
            }
        }
    },
    scales: {
        y: {
            beginAtZero: true,
            max: 5,
            ticks: {
                stepSize: 1,
                callback: function(value) {
                    const labels = ['', 'Very Low', 'Low', 'Neutral', 'Good', 'Excellent'];
                    return labels[value] || value;
                }
            },
            grid: {
                color: 'rgba(0, 0, 0, 0.1)'
            }
        },
        x: {
            grid: {
                color: 'rgba(0, 0, 0, 0.1)'
            }
        }
    },
    elements: {
        point: {
            radius: 6,
            hoverRadius: 8,
            borderWidth: 2,
            borderColor: '#fff'
        },
        line: {
            borderWidth: 3,
            tension: 0.4
        }
    }
};

/**
 * Color schemes for different mood ranges
 */
const MOOD_COLORS = {
    1: { bg: 'rgba(244, 67, 54, 0.1)', border: '#f44336' },    // Red - Very Low
    2: { bg: 'rgba(255, 152, 0, 0.1)', border: '#ff9800' },   // Orange - Low
    3: { bg: 'rgba(156, 39, 176, 0.1)', border: '#9c27b0' },  // Purple - Neutral
    4: { bg: 'rgba(76, 175, 80, 0.1)', border: '#4caf50' },   // Green - Good
    5: { bg: 'rgba(33, 150, 243, 0.1)', border: '#2196f3' }   // Blue - Excellent
};

/**
 * Create a mood trend chart
 */
function createMoodTrendChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas element with id "${canvasId}" not found`);
        return null;
    }

    const chartConfig = {
        type: 'line',
        data: {
            labels: data.labels || [],
            datasets: [{
                label: 'Mood Score',
                data: data.values || [],
                borderColor: '#2196F3',
                backgroundColor: 'rgba(33, 150, 243, 0.1)',
                fill: true,
                ...options.dataset
            }]
        },
        options: {
            ...MOOD_CHART_CONFIG,
            ...options.chartOptions
        }
    };

    return new Chart(ctx, chartConfig);
}

/**
 * Create an emotion breakdown chart (doughnut)
 */
function createEmotionChart(canvasId, emotions, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas element with id "${canvasId}" not found`);
        return null;
    }

    // Filter out emotions with very low values
    const filteredEmotions = Object.entries(emotions)
        .filter(([emotion, value]) => value > 5)
        .sort(([,a], [,b]) => b - a);

    const labels = filteredEmotions.map(([emotion]) => 
        emotion.charAt(0).toUpperCase() + emotion.slice(1)
    );
    const values = filteredEmotions.map(([, value]) => value);

    const emotionColors = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A',
        '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9',
        '#F8C471', '#AED6F1', '#A9DFBF', '#F5B7B1'
    ];

    const chartConfig = {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: emotionColors.slice(0, labels.length),
                borderWidth: 2,
                borderColor: '#fff',
                hoverBorderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    borderColor: 'rgba(255, 255, 255, 0.2)',
                    borderWidth: 1,
                    cornerRadius: 6,
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((context.parsed / total) * 100).toFixed(1);
                            return `${context.label}: ${percentage}%`;
                        }
                    }
                }
            },
            ...options
        }
    };

    return new Chart(ctx, chartConfig);
}

/**
 * Create a mood comparison chart (bar chart for comparing periods)
 */
function createMoodComparisonChart(canvasId, data, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) {
        console.error(`Canvas element with id "${canvasId}" not found`);
        return null;
    }

    const chartConfig = {
        type: 'bar',
        data: {
            labels: data.labels || [],
            datasets: data.datasets || []
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: data.datasets && data.datasets.length > 1
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: 'white',
                    bodyColor: 'white',
                    borderColor: 'rgba(255, 255, 255, 0.2)',
                    borderWidth: 1,
                    cornerRadius: 6
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 5,
                    ticks: {
                        stepSize: 1
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                x: {
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                }
            },
            ...options
        }
    };

    return new Chart(ctx, chartConfig);
}

/**
 * Fetch mood data from API
 */
async function fetchMoodData(timeframe = '90') {
    try {
        const response = await fetch(`/api/mood-data?timeframe=${timeframe}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching mood data:', error);
        if (window.MindCareUtils) {
            window.MindCareUtils.showToast('Failed to load mood data', 'danger');
        }
        return null;
    }
}

/**
 * Calculate mood statistics
 */
function calculateMoodStats(moodData) {
    if (!moodData || !moodData.mood_scores || moodData.mood_scores.length === 0) {
        return {
            average: 0,
            highest: 0,
            lowest: 0,
            trend: 'neutral',
            totalEntries: 0
        };
    }

    const scores = moodData.mood_scores;
    const average = scores.reduce((sum, score) => sum + score, 0) / scores.length;
    const highest = Math.max(...scores);
    const lowest = Math.min(...scores);
    
    // Calculate trend (comparing first half to second half)
    const halfPoint = Math.floor(scores.length / 2);
    const firstHalf = scores.slice(0, halfPoint);
    const secondHalf = scores.slice(halfPoint);
    
    const firstAvg = firstHalf.reduce((sum, score) => sum + score, 0) / firstHalf.length;
    const secondAvg = secondHalf.reduce((sum, score) => sum + score, 0) / secondHalf.length;
    
    let trend = 'neutral';
    const difference = secondAvg - firstAvg;
    if (difference > 0.3) trend = 'improving';
    else if (difference < -0.3) trend = 'declining';

    return {
        average: Math.round(average * 10) / 10,
        highest,
        lowest,
        trend,
        totalEntries: scores.length
    };
}

/**
 * Update mood statistics display
 */
function updateMoodStatsDisplay(stats) {
    const elements = {
        average: document.getElementById('mood-avg'),
        highest: document.getElementById('mood-highest'),
        lowest: document.getElementById('mood-lowest'),
        trend: document.getElementById('mood-trend'),
        total: document.getElementById('mood-total')
    };

    if (elements.average) {
        elements.average.textContent = stats.average.toFixed(1);
    }
    
    if (elements.highest) {
        elements.highest.textContent = stats.highest;
    }
    
    if (elements.lowest) {
        elements.lowest.textContent = stats.lowest;
    }
    
    if (elements.trend) {
        const trendText = {
            improving: '📈 Improving',
            declining: '📉 Declining', 
            neutral: '➡️ Stable'
        };
        elements.trend.textContent = trendText[stats.trend] || '➡️ Stable';
        
        const trendClass = {
            improving: 'text-success',
            declining: 'text-danger',
            neutral: 'text-info'
        };
        elements.trend.className = trendClass[stats.trend] || 'text-info';
    }
    
    if (elements.total) {
        elements.total.textContent = stats.totalEntries;
    }
}

/**
 * Initialize mood charts on page load
 */
function initializeMoodCharts() {
    const chartContainers = [
        { id: 'moodChart', type: 'trend' },
        { id: 'moodTrendChart', type: 'trend' },
        { id: 'emotionChart', type: 'emotion' },
        { id: 'moodComparisonChart', type: 'comparison' }
    ];

    chartContainers.forEach(container => {
        const element = document.getElementById(container.id);
        if (element) {
            initializeChart(container.id, container.type);
        }
    });
}

/**
 * Initialize individual chart
 */
async function initializeChart(chartId, chartType) {
    const loadingIndicator = showChartLoading(chartId);
    
    try {
        if (chartType === 'trend') {
            await initializeTrendChart(chartId);
        } else if (chartType === 'emotion') {
            await initializeEmotionChart(chartId);
        } else if (chartType === 'comparison') {
            await initializeComparisonChart(chartId);
        }
    } catch (error) {
        console.error(`Error initializing ${chartType} chart:`, error);
        showChartError(chartId);
    } finally {
        hideChartLoading(loadingIndicator);
    }
}

/**
 * Initialize trend chart
 */
async function initializeTrendChart(chartId) {
    const moodData = await fetchMoodData();
    if (!moodData) return;

    const chart = createMoodTrendChart(chartId, {
        labels: moodData.dates || [],
        values: moodData.mood_scores || []
    });

    // Update statistics if available
    const stats = calculateMoodStats(moodData);
    updateMoodStatsDisplay(stats);

    return chart;
}

/**
 * Initialize emotion chart
 */
async function initializeEmotionChart(chartId) {
    // For emotion charts, we'll use aggregated emotion data
    // This would typically come from the backend, but for now we'll use sample structure
    const emotionData = {
        happiness: 25,
        calm: 20,
        hope: 15,
        anxiety: 12,
        sadness: 10,
        excitement: 8,
        anger: 6,
        fear: 4
    };

    const chart = createEmotionChart(chartId, emotionData);
    return chart;
}

/**
 * Initialize comparison chart
 */
async function initializeComparisonChart(chartId) {
    // This would compare different time periods
    const comparisonData = {
        labels: ['This Week', 'Last Week', 'This Month', 'Last Month'],
        datasets: [{
            label: 'Average Mood',
            data: [3.8, 3.2, 3.5, 3.1],
            backgroundColor: 'rgba(33, 150, 243, 0.6)',
            borderColor: '#2196F3',
            borderWidth: 2
        }]
    };

    const chart = createMoodComparisonChart(chartId, comparisonData);
    return chart;
}

/**
 * Show loading indicator for chart
 */
function showChartLoading(chartId) {
    const container = document.getElementById(chartId).parentElement;
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'chart-loading position-absolute top-50 start-50 translate-middle';
    loadingDiv.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading chart...</span>
            </div>
            <p class="mt-2 text-muted">Loading chart data...</p>
        </div>
    `;
    
    container.style.position = 'relative';
    container.appendChild(loadingDiv);
    
    return loadingDiv;
}

/**
 * Hide loading indicator
 */
function hideChartLoading(loadingElement) {
    if (loadingElement && loadingElement.parentElement) {
        loadingElement.remove();
    }
}

/**
 * Show chart error
 */
function showChartError(chartId) {
    const canvas = document.getElementById(chartId);
    const container = canvas.parentElement;
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'chart-error text-center p-4';
    errorDiv.innerHTML = `
        <i data-feather="alert-circle" class="text-muted mb-2" style="width: 48px; height: 48px;"></i>
        <p class="text-muted">Unable to load chart data</p>
        <button class="btn btn-outline-primary btn-sm" onclick="retryChart('${chartId}')">
            <i data-feather="refresh-cw" class="me-1"></i>
            Retry
        </button>
    `;
    
    canvas.style.display = 'none';
    container.appendChild(errorDiv);
    
    // Replace feather icons
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
}

/**
 * Retry loading chart
 */
function retryChart(chartId) {
    const container = document.getElementById(chartId).parentElement;
    const errorElement = container.querySelector('.chart-error');
    if (errorElement) {
        errorElement.remove();
    }
    
    const canvas = document.getElementById(chartId);
    canvas.style.display = 'block';
    
    // Determine chart type and reinitialize
    const chartType = canvas.dataset.chartType || 'trend';
    initializeChart(chartId, chartType);
}

/**
 * Export chart as image
 */
function exportChartAsImage(chartId, filename = 'mood-chart.png') {
    const canvas = document.getElementById(chartId);
    if (canvas) {
        const link = document.createElement('a');
        link.download = filename;
        link.href = canvas.toDataURL();
        link.click();
    }
}

/**
 * Update chart time range
 */
async function updateChartTimeRange(chartId, timeframe) {
    const chart = Chart.getChart(chartId);
    if (!chart) return;

    const moodData = await fetchMoodData(timeframe);
    if (!moodData) return;

    chart.data.labels = moodData.dates || [];
    chart.data.datasets[0].data = moodData.mood_scores || [];
    chart.update();

    // Update statistics
    const stats = calculateMoodStats(moodData);
    updateMoodStatsDisplay(stats);
}

// Initialize charts when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Small delay to ensure all other scripts are loaded
    setTimeout(initializeMoodCharts, 100);
});

// Make functions available globally
window.MoodCharts = {
    createMoodTrendChart,
    createEmotionChart,
    createMoodComparisonChart,
    fetchMoodData,
    calculateMoodStats,
    updateMoodStatsDisplay,
    exportChartAsImage,
    updateChartTimeRange,
    retryChart
};
