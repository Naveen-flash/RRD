from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    product = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default="Processing")

