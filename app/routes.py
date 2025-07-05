from flask import Blueprint, render_template, jsonify, request, current_app
from app import mongo
import json
from bson import json_util
from flask_socketio import emit
from app import socketio
from datetime import datetime, timedelta


main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def dashboard():
    return render_template('dashboard.html')


@main_bp.route('/api/blocks/recent')
def recent_blocks():
    collection = mongo.get_collection('blocks')
    data = collection.find().sort('blockNumber', -1).limit(10)
    return json.loads(json_util.dumps(data))

@main_bp.route('/api/transactions/<block_number>')
def block_transactions(block_number):
    collection = mongo.get_collection('transactions')
    data = collection.find({'blockNumber': int(block_number)})
    return json.loads(json_util.dumps(data))

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@main_bp.route('/api/price/<symbol>')
def price_data(symbol):
    try:
        collection = mongo.get_collection('price_history')

        # Calcular timestamp de hace n horas
        hours = request.args.get('hours', default=24, type=int)
        time_range = datetime.utcnow() - timedelta(hours=hours)

        # Consultar solo datos de las últimas 24 horas
        data = collection.find({
            'symbol': symbol,
            'timestamp': {'$gte': time_range}
        }).sort('timestamp', 1)  # Orden ascendente para el gráfico

        return json.loads(json_util.dumps(data))
    except Exception as e:
        current_app.logger.error(f"Error en /api/price: {str(e)}")
        return jsonify({"error": "Database error"}), 500
                                                           
