document.addEventListener('DOMContentLoaded', function() {
    // Inicializar conexión SocketIO
    const socket = io();
    
    // Elementos DOM
    const priceChartCtx = document.getElementById('priceChart').getContext('2d');
    const blocksList = document.getElementById('blocks-list');
    const transactionsContainer = document.getElementById('transactions-container');
    
    // Variables de estado
    let priceChart = null;
    let currentBlock = null;
    let priceData = {
        labels: [],
        datasets: [{
            label: 'Precio ETH (USD)',
            data: [],
            borderColor: 'rgb(75, 192, 192)',
            backgroundColor: 'rgba(75, 192, 192, 0.1)',
            borderWidth: 2,
            tension: 0.1,
            fill: true
        }]
    };
    
    // 1. Inicializar gráfico de precios
    function initPriceChart() {
        return new Chart(priceChartCtx, {
            type: 'line',
            data: priceData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false,
                        grid: {
                            color: 'rgba(200, 200, 200, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            maxTicksLimit: 8
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
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
                interaction: {
                    intersect: false,
                    mode: 'nearest'
                }
            }
        });
    }
    
    // 2. Actualizar gráfico de precios
    function updatePriceChart(newData) {
        // Procesar nuevos datos
        newData.forEach(item => {
            const date = new Date(item.timestamp.$date);
            const label = date.toLocaleTimeString();
            const price = item.price;
            
            // Agregar nuevos datos
            priceData.labels.push(label);
            priceData.datasets[0].data.push(price);
            
            // Mantener solo los últimos 100 puntos
            if (priceData.labels.length > 100) {
                priceData.labels.shift();
                priceData.datasets[0].data.shift();
            }
        });
        
        // Actualizar gráfico
        if (priceChart) {
            priceChart.update();
        } else {
            priceChart = initPriceChart();
        }
    }
    
    // 3. Formatear timestamp
    function formatTimestamp(timestamp) {
        const date = new Date(timestamp.$date);
        return date.toLocaleTimeString();
    }
    
    // 4. Formatear dirección ETH
    function formatAddress(address) {
        return `${address.substring(0, 6)}...${address.substring(address.length - 4)}`;
    }
    
    // 5. Actualizar lista de bloques
    function updateRecentBlocksList(blocks) {
        blocksList.innerHTML = '';
        
        blocks.forEach(block => {
            const blockDate = new Date(block.timestamp.$date);
            const listItem = document.createElement('li');
            listItem.className = 'block-item';
            listItem.dataset.blockNumber = block.blockNumber;
            listItem.innerHTML = `
                <div class="block-header">
                    <span class="block-number">#${block.blockNumber}</span>
                    <span class="block-time">${blockDate.toLocaleTimeString()}</span>
                </div>
                <div class="block-hash">${formatAddress(block.hash)}</div>
                <div class="block-transactions">${block.transactions.length} transacciones</div>
            `;
            
            listItem.addEventListener('click', function() {
                loadBlockTransactions(block.blockNumber);
            });
            
            blocksList.appendChild(listItem);
        });
    }
    
    // 6. Cargar transacciones de un bloque
    function loadBlockTransactions(blockNumber) {
        // Resaltar bloque seleccionado
        document.querySelectorAll('.block-item').forEach(item => {
            item.classList.remove('active');
        });
        document.querySelector(`.block-item[data-block-number="${blockNumber}"]`).classList.add('active');
        
        fetch(`/api/transactions/${blockNumber}`)
            .then(response => response.json())
            .then(transactions => {
                renderTransactions(transactions);
            });
    }
    
    // 7. Renderizar transacciones
    function renderTransactions(transactions) {
        transactionsContainer.innerHTML = '';
        
        if (transactions.length === 0) {
            transactionsContainer.innerHTML = '<p>No hay transacciones en este bloque</p>';
            return;
        }
        
        const table = document.createElement('table');
        table.className = 'transactions-table';
        table.innerHTML = `
            <thead>
                <tr>
                    <th>Hash</th>
                    <th>De</th>
                    <th>A</th>
                    <th>Valor (ETH)</th>
                </tr>
            </thead>
            <tbody></tbody>
        `;
        
        const tbody = table.querySelector('tbody');
        
        transactions.forEach(tx => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="tx-hash">${formatAddress(tx.hash)}</td>
                <td class="tx-from">${tx.from ? formatAddress(tx.from) : 'SYSTEM'}</td>
                <td class="tx-to">${tx.to ? formatAddress(tx.to) : 'CONTRACT'}</td>
                <td class="tx-value">${parseFloat(tx.value).toFixed(4)}</td>
            `;
            tbody.appendChild(row);
        });
        
        transactionsContainer.appendChild(table);
    }
    
    // 8. Manejar eventos de SocketIO
    socket.on('new_price_ethereum', (data) => {
        console.log('Nuevo precio recibido:', data);
        
        // Convertir a formato compatible con MongoDB
        const formattedData = {
            symbol: data.symbol,
            price: data.price,
            timestamp: {
                $date: data.timestamp
            }
        };
    
        updatePriceChart([formattedData]);
    });
    socket.on('new_block', (block) => {
        // Actualizar lista de bloques
        fetch('/api/blocks/recent')
            .then(response => response.json())
            .then(data => updateRecentBlocksList(data));
        
        // Si es el bloque seleccionado, actualizar transacciones
        if (currentBlock === block.blockNumber) {
            loadBlockTransactions(block.blockNumber);
        }
    });
    
    // 9. Cargar datos iniciales
    function loadInitialData() {
        // Precios históricos
        fetch('/api/price/ethereum')
            .then(response => response.json())
            .then(data => {
                updatePriceChart(data.reverse()); // Datos más antiguos primero
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
