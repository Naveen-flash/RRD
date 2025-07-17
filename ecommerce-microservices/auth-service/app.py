from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import db, User
import bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['JWT_SECRET_KEY'] = 'super-secret-key'

db.init_app(app)
jwt = JWTManager(app)

# ✅ Add this route so browser visits work
@app.route('/', methods=['GET'])
def index():
    return jsonify(message="User Authentication Service is running!"), 200

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']

    if User.query.filter_by(username=username).first():
        return jsonify(message='User already exists'), 409

    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    new_user = User(username=username, password=hashed)
    db.session.add(new_user)
    db.session.commit()

    return jsonify(message='User created'), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()

    if not user or not bcrypt.checkpw(data['password'].encode('utf-8'), user.password):
        return jsonify(message='Invalid credentials'), 401

    access_token = create_access_token(identity=user.username)
    return jsonify(access_token=access_token)

@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user)

# ✅ Ensure database is created before the app runs
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)

