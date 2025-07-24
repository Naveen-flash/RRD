from flask import Flask, request, jsonify
import os
import signalimport sys
from datetime import datetime

app = Flask(__name__)

# In-memory storage for simplicity
products = [
    {"id": 1, "name": "Laptop", "price": 999.99, "category": "Electronics"},
    {"id": 2, "name": "Book", "price": 19.99, "category": "Education"},
    {"id": 3, "name": "Coffee Mug", "price": 12.99, "category": "Kitchen"}
]

next_id = 4

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    }), 200

# Get all products
@app.route('/products', methods=['GET'])
def get_products():
    return jsonify(products), 200

# Get product by ID
@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = next((p for p in products if p['id'] == product_id), None)

    if not product:
        return jsonify({'error': 'Product not found'}), 404

    return jsonify(product), 200

# Create new product
@app.route('/products', methods=['POST'])
def create_product():
    global next_id

    data = request.get_json()

    if not data or not all(key in data for key in ['name', 'price', 'category']):
        return jsonify({'error': 'Name, price, and category are required'}), 400

    new_product = {
        'id': next_id,
        'name': data['name'],
        'price': float(data['price']),
        'category': data['category']
    }

    products.append(new_product)
    next_id += 1

    return jsonify(new_product), 201

# Update product
@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = next((p for p in products if p['id'] == product_id), None)

    if not product:
        return jsonify({'error': 'Product not found'}), 404

    data = request.get_json()

    if 'name' in data:
        product['name'] = data['name']
    if 'price' in data:
        product['price'] = float(data['price'])
    if 'category' in data:
        product['category'] = data['category']

    return jsonify(product), 200

# Delete product
@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    global products

    product_index = next((i for i, p in enumerate(products) if p['id'] == product_id), None)

    if product_index is None:
        return jsonify({'error': 'Product not found'}), 404

    products.pop(product_index)
    return '', 204

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Graceful shutdown handler
def signal_handler(sig, frame):
    print('Received shutdown signal, exiting gracefully...')
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port, debug=False)
