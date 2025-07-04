document.addEventListener('DOMContentLoaded', function() {
    const socket = io();
    const priceChart = initPriceChart();
    
    // Actualización en tiempo real
    socket.on('new_price', (data) => {
        updatePriceChart(priceChart, data);
    });
    
    socket.on('new_block', (block) => {
        updateRecentBlocks(block);
    });
    
    // Cargar datos iniciales
    fetch('/api/price/ethereum')
        .then(response => response.json())
        .then(data => {
            updatePriceChart(priceChart, data);
        });
    
    fetch('/api/blocks/recent')
        .then(response => response.json())
        .then(data => {
            updateRecentBlocksList(data);
        });
});

function initPriceChart() {
    const ctx = document.getElementById('priceChart').getContext('2d');
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Precio ETH',
                data: [],
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

function updatePriceChart(chart, newData) {
    // Lógica para actualizar el gráfico con nuevos datos
    // ...
}
