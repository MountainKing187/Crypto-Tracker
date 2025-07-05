# Crypto-Tracker
*Monitoreo en tiempo real de criptomonedas y blockchain*


Crypto-Tracker es una solución completa para monitorear mercados cripto y actividad de blockchain en tiempo real. Combina datos de precios de múltiples exchanges con información directa de la blockchain de Ethereum.

### Características Principales
Gráficos interactivos de precios en tiempo real
* Actualizaciones instantáneas usando WebSockets
* Explorador de bloques y transacciones de Ethereum
* Almacenamiento persistente en MongoDB
* Dashboard web responsive

### Tecnologías Utilizadas 

| Componente	| Tecnologías |
|-------------|------------|
| Backend	| Python, Flask, Flask-SocketIO, Web3.py, Requests |
| Frontend	| HTML5, CSS3, JavaScript, Chart.js, Socket.IO Client |
| Base de Datos	| MongoDB |
| APIs	| CoinGecko API, Alchemy Web3 (Ethereum) |

Y a futuro se implentara la funcionalidad de un asistene IA

### Instalación y Uso
Requisitos Previos
* Python 3.8+
* MongoDB
* API key de CoinGecko y Alchemy

### API Endpoints
El servicio expone los siguientes endpoints:

|Endpoint |	Método |	Descripción |
|---------|--------|--------------|
|/api/price/<symbol>	| GET |	Datos históricos de precios (24h)
|/api/blocks/recent |	GET	| Últimos 10 bloques de Ethereum
|/api/transactions/<block>	| GET |	Transacciones de un bloque específico
