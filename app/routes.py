from flask import Blueprint, render_template, jsonify
from app import mongo
import json
from bson import json_util
from flask_socketio import emit
from app import socketio

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def dashboard():
    return render_template('dashboard.html')

@main_bp.route('/api/price')
def price_data(symbol):
    collection = mongo.get_collection('price_history')
    data = collection.find().sort('timestamp', -1).limit(100)
    return json.loads(json_util.dumps(data))

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
