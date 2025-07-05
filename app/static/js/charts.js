document.addEventListener('DOMContentLoaded', function() {
    const socket = io();
    
    // Configuración de gráficos por moneda
    const cryptoCharts = {
        ethereum: initChart('ethChart', 'Ethereum (ETH)', 'rgb(75, 192, 192)'),
        dogecoin: initChart('dogeChart', 'Dogecoin (DOGE)', 'rgb(153, 102, 255)'),
        bitcoin: initChart('btcChart', 'Bitcoin (BTC)', 'rgb(255, 159, 64)')
    };
    
    // Inicializar un gráfico
    function initChart(canvasId, label, borderColor) {
        const ctx = document.getElementById(canvasId).getContext('2d');
        return {
            chart: new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: label,
                        data: [],
                        borderColor: borderColor,
                        backgroundColor: borderColor.replace('rgb', 'rgba').replace(')', ', 0.1)'),
                        borderWidth: 2,
                        tension: 0.1,
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: false,
                            grid: { color: 'rgba(200, 200, 200, 0.1)' }
                        },
                        x: {
                            grid: { display: false },
                            ticks: { maxTicksLimit: 8 }
                        }
                    },
                    plugins: {
                        legend: { display: false },
                        tooltip: {
                            mode: 'index',
                            intersect: false,
                            callbacks: {
                                label: function(context) {
                                    return `$${context.parsed.y.toFixed(2)}`;
                                }
                            }
                        }
                    },
                    interaction: { intersect: false, mode: 'nearest' }
                }
            }),
            data: {
                labels: [],
                prices: []
            }
        };
    }
    
    // Actualizar un gráfico específico
    function updateChart(currency, newData) {
        const chartConfig = cryptoCharts[currency];
        if (!chartConfig) return;
        
        // Filtrar y validar datos
        const validData = newData.filter(item => {
            return item.symbol === currency &&
                   typeof item.price === 'number' && 
                   item.price > 0 &&
                   item.timestamp;
        });
        
        if (validData.length === 0) return;
        
        // Ordenar por timestamp (más antiguo primero)
        validData.sort((a, b) => {
            const dateA = a.timestamp.$date ? new Date(a.timestamp.$date) : new Date(a.timestamp);
            const dateB = b.timestamp.$date ? new Date(b.timestamp.$date) : new Date(b.timestamp);
            return dateA - dateB;
        });
        
        // Procesar nuevos datos
        validData.forEach(item => {
            const dateObj = item.timestamp.$date ? 
                new Date(item.timestamp.$date) : 
                new Date(item.timestamp);
                
            const label = dateObj.toLocaleTimeString();
            const price = item.price;
            
            // Solo añadir si es un nuevo dato o precio diferente
            const lastPrice = chartConfig.data.prices[chartConfig.data.prices.length - 1];
            if (chartConfig.data.prices.length === 0 || price !== lastPrice) {
                chartConfig.data.labels.push(label);
                chartConfig.data.prices.push(price);
                
                // Mantener solo los últimos 100 puntos
                if (chartConfig.data.labels.length > 100) {
                    chartConfig.data.labels.shift();
                    chartConfig.data.prices.shift();
                }
            }
        });
        
        // Actualizar el gráfico
        chartConfig.chart.data.labels = chartConfig.data.labels;
        chartConfig.chart.data.datasets[0].data = chartConfig.data.prices;
        chartConfig.chart.update();
    }
    
    // Eventos de SocketIO para cada moneda
    socket.on('new_price_ethereum', (data) => {
        if (data.symbol === 'ethereum') {
            updateChart('ethereum', [data]);
        }
    });
    
    socket.on('new_price_dogecoin', (data) => {
        if (data.symbol === 'dogecoin') {
            updateChart('dogecoin', [data]);
        }
    });
    
    socket.on('new_price_bitcoin', (data) => {
        if (data.symbol === 'bitcoin') {
            updateChart('bitcoin', [data]);
        }
    });
    
    // Cargar datos iniciales para cada moneda
    function loadInitialData() {
        // Ethereum
        fetch('/api/price/ethereum')
            .then(response => response.json())
            .then(data => {
                updateChart('ethereum', data.reverse());
            });
        
        // Dogecoin
        fetch('/api/price/dogecoin')
            .then(response => response.json())
            .then(data => {
                updateChart('dogecoin', data.reverse());
            });
        
        // Bitcoin
        fetch('/api/price/bitcoin')
            .then(response => response.json())
            .then(data => {
                updateChart('bitcoin', data.reverse());
            });
        
        // Bloques recientes
        fetch('/api/blocks/recent')
            .then(response => response.json())
            .then(data => {
                updateRecentBlocksList(data);
                if (data.length > 0) {
                    currentBlock = data[0].blockNumber;
                    loadBlockTransactions(currentBlock);
                }
            });
    }
    
    // Inicializar la aplicación
    priceChart = initPriceChart();
    loadInitialData();
});
