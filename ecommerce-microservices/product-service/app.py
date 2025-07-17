# Product Management Service
# File: product-service/app.py

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import logging

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///products.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Product model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    category = db.Column(db.String(50))
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'stock': self.stock,
            'category': self.category
        }

# Create tables
with app.app_context():
    db.create_all()
    
    # Add sample data if the table is empty
    if Product.query.count() == 0:
        sample_products = [
            Product(name='Laptop', description='High-performance laptop', price=999.99, stock=10, category='Electronics'),
            Product(name='Smartphone', description='Latest smartphone', price=699.99, stock=25, category='Electronics'),
            Product(name='Book', description='Programming book', price=29.99, stock=50, category='Books'),
            Product(name='Headphones', description='Wireless headphones', price=199.99, stock=15, category='Electronics'),
            Product(name='Coffee Mug', description='Ceramic coffee mug', price=12.99, stock=100, category='Home')
        ]
        for product in sample_products:
            db.session.add(product)
        db.session.commit()
        logger.info("Sample products added to database")

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'product-service'}), 200

# Get all products
@app.route('/products', methods=['GET'])
def get_products():
    try:
        # Support for pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        category = request.args.get('category')
        
        query = Product.query
        if category:
            query = query.filter(Product.category == category)
        
        products = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'products': [product.to_dict() for product in products.items],
            'total': products.total,
            'pages': products.pages,
            'current_page': page
        }), 200
    except Exception as e:
        logger.error(f"Error fetching products: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Get product by ID
@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        return jsonify(product.to_dict()), 200
    except Exception as e:
        logger.error(f"Error fetching product {product_id}: {str(e)}")
        return jsonify({'error': 'Product not found'}), 404

# Create new product
@app.route('/products', methods=['POST'])
def create_product():
    try:
        data = request.get_json()
        
        # Validation
        required_fields = ['name', 'price']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        if data['price'] < 0:
            return jsonify({'error': 'Price cannot be negative'}), 400
        
        if data.get('stock', 0) < 0:
            return jsonify({'error': 'Stock cannot be negative'}), 400
        
        product = Product(
            name=data['name'],
            description=data.get('description', ''),
            price=data['price'],
            stock=data.get('stock', 0),
            category=data.get('category', '')
        )
        
        db.session.add(product)
        db.session.commit()
        
        logger.info(f"Product created: {product.name}")
        return jsonify(product.to_dict()), 201
        
    except Exception as e:
        logger.error(f"Error creating product: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Update product
@app.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        data = request.get_json()
        
        # Validation
        if 'price' in data and data['price'] < 0:
            return jsonify({'error': 'Price cannot be negative'}), 400
        
        if 'stock' in data and data['stock'] < 0:
            return jsonify({'error': 'Stock cannot be negative'}), 400
        
        product.name = data.get('name', product.name)
        product.description = data.get('description', product.description)
        product.price = data.get('price', product.price)
        product.stock = data.get('stock', product.stock)
        product.category = data.get('category', product.category)
        
        db.session.commit()
        
        logger.info(f"Product updated: {product.name}")
        return jsonify(product.to_dict()), 200
        
    except Exception as e:
        logger.error(f"Error updating product {product_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Delete product
@app.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        
        logger.info(f"Product deleted: {product_id}")
        return jsonify({'message': 'Product deleted successfully'}), 200
        
    except Exception as e:
        logger.error(f"Error deleting product {product_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Check product stock
@app.route('/products/<int:product_id>/stock', methods=['GET'])
def check_stock(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        return jsonify({'product_id': product_id, 'stock': product.stock}), 200
    except Exception as e:
        logger.error(f"Error checking stock for product {product_id}: {str(e)}")
        return jsonify({'error': 'Product not found'}), 404

# Update stock (for order processing)
@app.route('/products/<int:product_id>/stock', methods=['PUT'])
def update_stock(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        data = request.get_json()
        
        if 'stock' not in data:
            return jsonify({'error': 'Stock value required'}), 400
        
        if data['stock'] < 0:
            return jsonify({'error': 'Stock cannot be negative'}), 400
        
        product.stock = data['stock']
        db.session.commit()
        
        logger.info(f"Stock updated for product {product_id}: {product.stock}")
        return jsonify({'product_id': product_id, 'stock': product.stock}), 200
        
    except Exception as e:
        logger.error(f"Error updating stock for product {product_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Reduce stock (for order processing)
@app.route('/products/<int:product_id>/reduce-stock', methods=['POST'])
def reduce_stock(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        data = request.get_json()
        
        if 'quantity' not in data:
            return jsonify({'error': 'Quantity required'}), 400
        
        quantity = data['quantity']
        if quantity <= 0:
            return jsonify({'error': 'Quantity must be positive'}), 400
        
        if product.stock < quantity:
            return jsonify({'error': 'Insufficient stock'}), 400
        
        product.stock -= quantity
        db.session.commit()
        
        logger.info(f"Stock reduced for product {product_id}: -{quantity}, remaining: {product.stock}")
        return jsonify({
            'product_id': product_id,
            'quantity_reduced': quantity,
            'remaining_stock': product.stock
        }), 200
        
    except Exception as e:
        logger.error(f"Error reducing stock for product {product_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Get products by category
@app.route('/products/category/<category>', methods=['GET'])
def get_products_by_category(category):
    try:
        products = Product.query.filter_by(category=category).all()
        return jsonify([product.to_dict() for product in products]), 200
    except Exception as e:
        logger.error(f"Error fetching products by category {category}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Search products
@app.route('/products/search', methods=['GET'])
def search_products():
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'error': 'Search query required'}), 400
        
        products = Product.query.filter(
            Product.name.contains(query) | 
            Product.description.contains(query) |
            Product.category.contains(query)
        ).all()
        
        return jsonify([product.to_dict() for product in products]), 200
    except Exception as e:
        logger.error(f"Error searching products: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
