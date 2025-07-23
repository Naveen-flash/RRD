from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import datetime
import os
import logging
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuration
PORT = int(os.environ.get('PORT', 3000))
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# In-memory storage (in production, use a database like PostgreSQL/MongoDB)
orders = {}
order_items = {}

# Order status constants
class OrderStatus:
    PENDING = 'pending'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    CANCELLED = 'cancelled'

class Order:
    def __init__(self, customer_id: str, items: List[Dict], shipping_address: Dict, payment_method: str):
        self.id = str(uuid.uuid4())
        self.customer_id = customer_id
        self.items = items
        self.shipping_address = shipping_address
        self.payment_method = payment_method
        self.status = OrderStatus.PENDING
        self.total_amount = self.calculate_total()
        self.created_at = datetime.datetime.utcnow().isoformat()
        self.updated_at = self.created_at

    def calculate_total(self) -> float:
        return sum(item.get('price', 0) * item.get('quantity', 1) for item in self.items)

    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'items': self.items,
            'shipping_address': self.shipping_address,
            'payment_method': self.payment_method,
            'status': self.status,
            'total_amount': self.total_amount,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def update_status(self, new_status: str):
        if new_status in [OrderStatus.PENDING, OrderStatus.PROCESSING,
                         OrderStatus.SHIPPED, OrderStatus.DELIVERED, OrderStatus.CANCELLED]:
            self.status = new_status
            self.updated_at = datetime.datetime.utcnow().isoformat()
            logger.info(f"Order {self.id} status updated to {new_status}")

# Function to create sample orders
def create_sample_orders():
    """Create sample orders when the app starts"""
    sample_orders_data = [
        {
            "customer_id": "customer_001",
            "items": [
                {
                    "product_id": "prod_123",
                    "name": "Wireless Headphones",
                    "price": 99.99,
                    "quantity": 1
                },
                {
                    "product_id": "prod_124",
                    "name": "Phone Case",
                    "price": 19.99,
                    "quantity": 2
                }
            ],
            "shipping_address": {
                "street": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip_code": "10001",
                "country": "USA"
            },
            "payment_method": "credit_card"
        },
        {
            "customer_id": "customer_002",
            "items": [
                {
                    "product_id": "prod_125",
                    "name": "Laptop Stand",
                    "price": 45.50,
                    "quantity": 1
                }
            ],
            "shipping_address": {
                "street": "456 Oak Ave",
                "city": "Los Angeles",
                "state": "CA",
                "zip_code": "90210",
                "country": "USA"
            },
            "payment_method": "paypal"
        },
        {
            "customer_id": "customer_003",
            "items": [
                {
                    "product_id": "prod_126",
                    "name": "Coffee Mug",
                    "price": 12.99,
                    "quantity": 3
                },
                {
                    "product_id": "prod_127",
                    "name": "Notebook Set",
                    "price": 24.99,
                    "quantity": 1
                }
            ],
            "shipping_address": {
                "street": "789 Pine Rd",
                "city": "Chicago",
                "state": "IL",
                "zip_code": "60601",
                "country": "USA"
            },
            "payment_method": "debit_card"
        },
        {
            "customer_id": "customer_001",
            "items": [
                {
                    "product_id": "prod_128",
                    "name": "USB Cable",
                    "price": 15.99,
                    "quantity": 2
                },
                {
                    "product_id": "prod_129",
                    "name": "Power Bank",
                    "price": 35.99,
                    "quantity": 1
                }
            ],
            "shipping_address": {
                "street": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip_code": "10001",
                "country": "USA"
            },
            "payment_method": "credit_card"
        },
        {
            "customer_id": "customer_004",
            "items": [
                {
                    "product_id": "prod_130",
                    "name": "Bluetooth Speaker",
                    "price": 79.99,
                    "quantity": 1
                },
                {
                    "product_id": "prod_131",
                    "name": "Screen Cleaner Kit",
                    "price": 8.99,
                    "quantity": 1
                },
                {
                    "product_id": "prod_132",
                    "name": "Desk Organizer",
                    "price": 22.50,
                    "quantity": 1
                }
            ],
            "shipping_address": {
                "street": "321 Elm St",
                "city": "Miami",
                "state": "FL",
                "zip_code": "33101",
                "country": "USA"
            },
            "payment_method": "apple_pay"
        },
        {
            "customer_id": "customer_005",
            "items": [
                {
                    "product_id": "prod_133",
                    "name": "Gaming Mouse",
                    "price": 59.99,
                    "quantity": 1
                }
            ],
            "shipping_address": {
                "street": "654 Broadway",
                "city": "Seattle",
                "state": "WA",
                "zip_code": "98101",
                "country": "USA"
            },
            "payment_method": "google_pay"
        },
        {
            "customer_id": "customer_002",
            "items": [
                {
                    "product_id": "prod_134",
                    "name": "Wireless Charger",
                    "price": 29.99,
                    "quantity": 2
                }
            ],
            "shipping_address": {
                "street": "456 Oak Ave",
                "city": "Los Angeles",
                "state": "CA",
                "zip_code": "90210",
                "country": "USA"
            },
            "payment_method": "paypal"
        }
    ]

    # Create orders from sample data
    for order_data in sample_orders_data:
        order = Order(
            customer_id=order_data['customer_id'],
            items=order_data['items'],
            shipping_address=order_data['shipping_address'],
            payment_method=order_data['payment_method']
        )
        orders[order.id] = order
        logger.info(f"Sample order created: {order.id} for customer: {order_data['customer_id']}")

    # Update some orders to different statuses for variety
    order_list = list(orders.values())
    if len(order_list) >= 5:
        order_list[1].update_status(OrderStatus.PROCESSING)
        order_list[2].update_status(OrderStatus.SHIPPED)
        order_list[3].update_status(OrderStatus.DELIVERED)
        order_list[4].update_status(OrderStatus.CANCELLED)

    logger.info(f"Created {len(orders)} sample orders with various statuses")

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.utcnow().isoformat(),
        'service': 'order-processing-service',
        'version': '1.0.0'
    })

# Readiness probe for Kubernetes
@app.route('/ready', methods=['GET'])
def readiness_check():
    return jsonify({
        'status': 'ready',
        'timestamp': datetime.datetime.utcnow().isoformat()
    })

# Create a new order
@app.route('/orders', methods=['POST'])
def create_order():
    try:
        data = request.get_json()

        # Validation
        required_fields = ['customer_id', 'items', 'shipping_address', 'payment_method']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        if not isinstance(data['items'], list) or len(data['items']) == 0:
            return jsonify({'error': 'Items must be a non-empty list'}), 400

        # Validate items structure
        for item in data['items']:
            if not all(key in item for key in ['product_id', 'name', 'price', 'quantity']):
                return jsonify({'error': 'Each item must have product_id, name, price, and quantity'}), 400

        # Create order
        order = Order(
            customer_id=data['customer_id'],
            items=data['items'],
            shipping_address=data['shipping_address'],
            payment_method=data['payment_method']
        )

        orders[order.id] = order
        logger.info(f"New order created: {order.id} for customer: {data['customer_id']}")

        return jsonify({
            'message': 'Order created successfully',
            'order': order.to_dict()
        }), 201

    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Get all orders
@app.route('/orders', methods=['GET'])
def get_orders():
    try:
        customer_id = request.args.get('customer_id')
        status = request.args.get('status')

        filtered_orders = list(orders.values())

        if customer_id:
            filtered_orders = [order for order in filtered_orders if order.customer_id == customer_id]

        if status:
            filtered_orders = [order for order in filtered_orders if order.status == status]

        return jsonify({
            'orders': [order.to_dict() for order in filtered_orders],
            'count': len(filtered_orders)
        })

    except Exception as e:
        logger.error(f"Error retrieving orders: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Get order by ID
@app.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    try:
        order = orders.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404

        return jsonify({'order': order.to_dict()})

    except Exception as e:
        logger.error(f"Error retrieving order {order_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Update order status
@app.route('/orders/<order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    try:
        data = request.get_json()

        if 'status' not in data:
            return jsonify({'error': 'Status is required'}), 400

        order = orders.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404

        new_status = data['status']
        valid_statuses = [OrderStatus.PENDING, OrderStatus.PROCESSING,
                         OrderStatus.SHIPPED, OrderStatus.DELIVERED, OrderStatus.CANCELLED]

        if new_status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Valid statuses: {valid_statuses}'}), 400

        order.update_status(new_status)

        return jsonify({
            'message': 'Order status updated successfully',
            'order': order.to_dict()
        })

    except Exception as e:
        logger.error(f"Error updating order status {order_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Cancel order
@app.route('/orders/<order_id>/cancel', methods=['PUT'])
def cancel_order(order_id):
    try:
        order = orders.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404

        if order.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
            return jsonify({'error': 'Cannot cancel shipped or delivered orders'}), 400

        order.update_status(OrderStatus.CANCELLED)

        return jsonify({
            'message': 'Order cancelled successfully',
            'order': order.to_dict()
        })

    except Exception as e:
        logger.error(f"Error cancelling order {order_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Get order statistics
@app.route('/orders/stats', methods=['GET'])
def get_order_stats():
    try:
        total_orders = len(orders)
        status_counts = {}
        total_revenue = 0

        for order in orders.values():
            status = order.status
            status_counts[status] = status_counts.get(status, 0) + 1
            if order.status != OrderStatus.CANCELLED:
                total_revenue += order.total_amount

        return jsonify({
            'total_orders': total_orders,
            'status_breakdown': status_counts,
            'total_revenue': total_revenue,
            'average_order_value': total_revenue / max(total_orders, 1)
        })

    except Exception as e:
        logger.error(f"Error getting order statistics: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed'}), 405

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Create sample orders when the app starts
    create_sample_orders()

    logger.info(f"Starting Order Processing Service on port {PORT}")
    logger.info(f"Sample orders created: {len(orders)} orders loaded")
    app.run(host='0.0.0.0', port=PORT, debug=DEBUG)
