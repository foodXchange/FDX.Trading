// Modern Dashboard with Data Visualization

// Chart.js configuration
Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
Chart.defaults.color = '#4b5563';
Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(31, 41, 55, 0.95)';
Chart.defaults.plugins.tooltip.padding = 12;
Chart.defaults.plugins.tooltip.cornerRadius = 8;
Chart.defaults.plugins.tooltip.titleFont.size = 14;
Chart.defaults.plugins.tooltip.bodyFont.size = 13;

class DashboardCharts {
    constructor() {
        this.charts = {};
        this.init();
    }

    init() {
        // Wait for DOM
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.createCharts());
        } else {
            this.createCharts();
        }

        // Update charts on theme change
        window.addEventListener('themechange', () => this.updateChartsTheme());
    }

    createCharts() {
        // 1. Procurement Overview Chart
        this.createProcurementChart();
        
        // 2. Console Status Distribution
        this.createConsoleStatusChart();
        
        // 3. Monthly Trend Chart
        this.createTrendChart();
        
        // 4. Supplier Performance Chart
        this.createSupplierChart();
        
        // 5. Category Distribution
        this.createCategoryChart();
        
        // 6. Real-time Activity Feed
        this.createActivityFeed();
    }

    createProcurementChart() {
        const canvas = document.getElementById('procurementChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        
        // Gradient backgrounds
        const gradientGreen = ctx.createLinearGradient(0, 0, 0, 400);
        gradientGreen.addColorStop(0, 'rgba(16, 185, 129, 0.8)');
        gradientGreen.addColorStop(1, 'rgba(16, 185, 129, 0.2)');
        
        const gradientBlue = ctx.createLinearGradient(0, 0, 0, 400);
        gradientBlue.addColorStop(0, 'rgba(59, 130, 246, 0.8)');
        gradientBlue.addColorStop(1, 'rgba(59, 130, 246, 0.2)');
        
        const gradientPurple = ctx.createLinearGradient(0, 0, 0, 400);
        gradientPurple.addColorStop(0, 'rgba(147, 51, 234, 0.8)');
        gradientPurple.addColorStop(1, 'rgba(147, 51, 234, 0.2)');

        this.charts.procurement = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Active Requests', 'Pending Consoles', 'Completed Orders'],
                datasets: [{
                    label: 'Count',
                    data: [45, 28, 132],
                    backgroundColor: [gradientBlue, gradientPurple, gradientGreen],
                    borderColor: ['#3b82f6', '#9333ea', '#10b981'],
                    borderWidth: 2,
                    borderRadius: 8,
                    barThickness: 60
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.parsed.y + ' items';
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            display: true,
                            drawBorder: false,
                            color: 'rgba(156, 163, 175, 0.1)'
                        },
                        ticks: {
                            padding: 10
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            padding: 10
                        }
                    }
                }
            }
        });
    }

    createConsoleStatusChart() {
        const canvas = document.getElementById('consoleStatusChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        
        this.charts.consoleStatus = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Active', 'In Progress', 'Completed', 'On Hold'],
                datasets: [{
                    data: [35, 25, 30, 10],
                    backgroundColor: [
                        '#10b981',
                        '#3b82f6',
                        '#6b7280',
                        '#f59e0b'
                    ],
                    borderWidth: 0,
                    spacing: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 15,
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });

        // Add center text
        const centerText = document.createElement('div');
        centerText.style.cssText = 'position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center;';
        centerText.innerHTML = '<div style="font-size: 32px; font-weight: 700;">100</div><div style="font-size: 14px; color: #6b7280;">Total Consoles</div>';
        canvas.parentElement.style.position = 'relative';
        canvas.parentElement.appendChild(centerText);
    }

    createTrendChart() {
        const canvas = document.getElementById('trendChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        
        // Create gradient
        const gradient = ctx.createLinearGradient(0, 0, 0, 400);
        gradient.addColorStop(0, 'rgba(99, 102, 241, 0.4)');
        gradient.addColorStop(1, 'rgba(99, 102, 241, 0.05)');

        this.charts.trend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                datasets: [{
                    label: 'Procurement Volume ($M)',
                    data: [2.5, 3.2, 2.8, 4.1, 3.9, 5.2, 4.8, 6.1, 5.5, 7.2, 6.8, 8.5],
                    borderColor: '#6366f1',
                    backgroundColor: gradient,
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    pointBackgroundColor: '#6366f1',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
                }, {
                    label: 'Savings ($M)',
                    data: [0.3, 0.4, 0.35, 0.52, 0.48, 0.65, 0.6, 0.76, 0.69, 0.9, 0.85, 1.06],
                    borderColor: '#10b981',
                    borderWidth: 3,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    pointBackgroundColor: '#10b981',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        align: 'end',
                        labels: {
                            usePointStyle: true,
                            padding: 15
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': $' + context.parsed.y + 'M';
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            display: true,
                            drawBorder: false,
                            color: 'rgba(156, 163, 175, 0.1)'
                        },
                        ticks: {
                            padding: 10,
                            callback: function(value) {
                                return '$' + value + 'M';
                            }
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            padding: 10
                        }
                    }
                }
            }
        });
    }

    createSupplierChart() {
        const canvas = document.getElementById('supplierChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');

        this.charts.supplier = new Chart(ctx, {
            type: 'radar',
            data: {
                labels: ['Quality', 'Delivery', 'Price', 'Service', 'Innovation', 'Reliability'],
                datasets: [{
                    label: 'Top Performer',
                    data: [95, 88, 82, 91, 78, 94],
                    borderColor: '#6366f1',
                    backgroundColor: 'rgba(99, 102, 241, 0.2)',
                    borderWidth: 2,
                    pointRadius: 4,
                    pointBackgroundColor: '#6366f1'
                }, {
                    label: 'Average',
                    data: [75, 72, 78, 70, 65, 73],
                    borderColor: '#6b7280',
                    backgroundColor: 'rgba(107, 114, 128, 0.1)',
                    borderWidth: 2,
                    borderDash: [5, 5],
                    pointRadius: 4,
                    pointBackgroundColor: '#6b7280'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'bottom',
                        labels: {
                            usePointStyle: true,
                            padding: 15
                        }
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        max: 100,
                        ticks: {
                            stepSize: 20,
                            display: false
                        },
                        grid: {
                            color: 'rgba(156, 163, 175, 0.2)'
                        },
                        pointLabels: {
                            font: {
                                size: 12
                            }
                        }
                    }
                }
            }
        });
    }

    createCategoryChart() {
        const canvas = document.getElementById('categoryChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');

        this.charts.category = new Chart(ctx, {
            type: 'polarArea',
            data: {
                labels: ['Pasta', 'Cereals', 'Dairy', 'Beverages', 'Snacks', 'Frozen'],
                datasets: [{
                    data: [45, 38, 52, 29, 41, 35],
                    backgroundColor: [
                        'rgba(239, 68, 68, 0.7)',
                        'rgba(245, 158, 11, 0.7)',
                        'rgba(16, 185, 129, 0.7)',
                        'rgba(59, 130, 246, 0.7)',
                        'rgba(147, 51, 234, 0.7)',
                        'rgba(236, 72, 153, 0.7)'
                    ],
                    borderColor: [
                        '#ef4444',
                        '#f59e0b',
                        '#10b981',
                        '#3b82f6',
                        '#9333ea',
                        '#ec4899'
                    ],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            padding: 12,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return context.label + ': ' + context.parsed.r + ' orders';
                            }
                        }
                    }
                },
                scales: {
                    r: {
                        beginAtZero: true,
                        ticks: {
                            display: false
                        },
                        grid: {
                            color: 'rgba(156, 163, 175, 0.2)'
                        }
                    }
                }
            }
        });
    }

    createActivityFeed() {
        const feed = document.getElementById('activityFeed');
        if (!feed) return;

        const activities = [
            { type: 'success', icon: '✓', text: 'New console CON-2025-0002 created', time: '2 mins ago' },
            { type: 'info', icon: '📦', text: '40 containers of pasta order approved', time: '15 mins ago' },
            { type: 'warning', icon: '⚠', text: 'Price alert: Cereals up 5%', time: '1 hour ago' },
            { type: 'success', icon: '🤝', text: 'Supplier Metro Foods verified', time: '2 hours ago' },
            { type: 'info', icon: '📈', text: 'Monthly savings target achieved', time: '3 hours ago' }
        ];

        feed.innerHTML = activities.map(activity => `
            <div class="activity-item" style="display: flex; align-items: start; gap: 12px; padding: 12px; border-radius: 8px; margin-bottom: 8px; background: var(--bg-surface); transition: all 0.2s;">
                <div class="activity-icon" style="width: 32px; height: 32px; border-radius: 50%; background: ${activity.type === 'success' ? '#10b98120' : activity.type === 'warning' ? '#f59e0b20' : '#3b82f620'}; display: flex; align-items: center; justify-content: center; font-size: 16px;">
                    ${activity.icon}
                </div>
                <div style="flex: 1;">
                    <div style="font-size: 14px; color: var(--text-primary); margin-bottom: 4px;">${activity.text}</div>
                    <div style="font-size: 12px; color: var(--text-secondary);">${activity.time}</div>
                </div>
            </div>
        `).join('');

        // Add hover effect
        feed.querySelectorAll('.activity-item').forEach(item => {
            item.addEventListener('mouseenter', function() {
                this.style.transform = 'translateX(4px)';
                this.style.boxShadow = '0 2px 8px rgba(0,0,0,0.1)';
            });
            item.addEventListener('mouseleave', function() {
                this.style.transform = 'translateX(0)';
                this.style.boxShadow = 'none';
            });
        });
    }

    updateChartsTheme() {
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        
        // Update chart colors based on theme
        Object.values(this.charts).forEach(chart => {
            if (chart) {
                chart.options.plugins.legend.labels.color = isDark ? '#e0e1dd' : '#4b5563';
                chart.options.scales?.y?.ticks && (chart.options.scales.y.ticks.color = isDark ? '#a8a9a5' : '#6b7280');
                chart.options.scales?.x?.ticks && (chart.options.scales.x.ticks.color = isDark ? '#a8a9a5' : '#6b7280');
                chart.options.scales?.r?.pointLabels && (chart.options.scales.r.pointLabels.color = isDark ? '#a8a9a5' : '#6b7280');
                chart.update();
            }
        });
    }

    // Real-time data updates
    startRealTimeUpdates() {
        setInterval(() => {
            // Update procurement chart with random data
            if (this.charts.procurement) {
                this.charts.procurement.data.datasets[0].data = [
                    45 + Math.floor(Math.random() * 10),
                    28 + Math.floor(Math.random() * 10),
                    132 + Math.floor(Math.random() * 20)
                ];
                this.charts.procurement.update();
            }

            // Add new activity
            this.addNewActivity();
        }, 30000); // Update every 30 seconds
    }

    addNewActivity() {
        const feed = document.getElementById('activityFeed');
        if (!feed) return;

        const newActivities = [
            { type: 'success', icon: '✓', text: 'New request submitted', time: 'Just now' },
            { type: 'info', icon: '📊', text: 'Weekly report generated', time: 'Just now' },
            { type: 'warning', icon: '🔔', text: 'Inventory alert triggered', time: 'Just now' }
        ];

        const activity = newActivities[Math.floor(Math.random() * newActivities.length)];
        
        const newItem = document.createElement('div');
        newItem.className = 'activity-item';
        newItem.style.cssText = 'display: flex; align-items: start; gap: 12px; padding: 12px; border-radius: 8px; margin-bottom: 8px; background: var(--bg-surface); transition: all 0.2s; animation: slideIn 0.3s ease-out;';
        newItem.innerHTML = `
            <div class="activity-icon" style="width: 32px; height: 32px; border-radius: 50%; background: ${activity.type === 'success' ? '#10b98120' : activity.type === 'warning' ? '#f59e0b20' : '#3b82f620'}; display: flex; align-items: center; justify-content: center; font-size: 16px;">
                ${activity.icon}
            </div>
            <div style="flex: 1;">
                <div style="font-size: 14px; color: var(--text-primary); margin-bottom: 4px;">${activity.text}</div>
                <div style="font-size: 12px; color: var(--text-secondary);">${activity.time}</div>
            </div>
        `;

        feed.insertBefore(newItem, feed.firstChild);

        // Remove old items if too many
        while (feed.children.length > 5) {
            feed.removeChild(feed.lastChild);
        }
    }
}

// Initialize dashboard charts
window.dashboardCharts = new DashboardCharts();

// Start real-time updates
window.dashboardCharts.startRealTimeUpdates();