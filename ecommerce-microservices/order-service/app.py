from flask import Flask, request, jsonify
from models import db, Order

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/', methods=['GET'])
def home():
    return jsonify(message="Order Processing Service is running!"), 200

@app.route('/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    order = Order(
        customer_name=data['customer_name'],
        product=data['product'],
        quantity=data['quantity']
    )
    db.session.add(order)
    db.session.commit()
    return jsonify(message="Order created", order_id=order.id), 201

@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = Order.query.get(order_id)
    if order:
        return jsonify(
            id=order.id,
            customer_name=order.customer_name,
            product=order.product,
            quantity=order.quantity,
            status=order.status
        )
    return jsonify(message="Order not found"), 404

@app.route('/orders', methods=['GET'])
def list_orders():
    orders = Order.query.all()
    return jsonify([
        {
            "id": o.id,
            "customer_name": o.customer_name,
            "product": o.product,
            "quantity": o.quantity,
            "status": o.status
        }
        for o in orders
    ])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)

