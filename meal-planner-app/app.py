import os
import json
import requests
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='/static')

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{os.getenv('DATABASE_USER')}:{os.getenv('DATABASE_PASSWORD')}"
    f"@{os.getenv('DATABASE_HOST')}:{os.getenv('DATABASE_PORT')}/{os.getenv('DATABASE_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Models ---
class Product(db.Model):
    __tablename__ = 'paragony_pozycje'
    
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column('produkt', db.String(200))
    category = db.Column('kategoria', db.String(100))
    quantity = db.Column('ilosc', db.Numeric)
    price = db.Column('cena_jedn', db.Numeric)
    expiry_date = db.Column('data_waznosci', db.Date)
    available = db.Column('dostepny', db.String(10)) # TAK/NIE
    is_frozen = db.Column('czy_mrozonka', db.Boolean, default=False)
    shop = db.Column('sklep', db.String(100))
    purchase_date = db.Column('data_zakupow', db.Date)
    
    # Virtual field for unit (defaults to 'szt' as it's missing in DB)
    unit = 'szt'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name or "Nieznany produkt",
            'category': self.category,
            # Handle numeric conversion safely
            'quantity': float(self.quantity) if self.quantity else 0.0,
            'unit': self.unit,
            'price': float(self.price) if self.price else 0.0,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'available': self.available,
            'is_frozen': bool(self.is_frozen),
            'shop': self.shop
        }

class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    ingredients = db.Column(db.Text) # Stored as JSON string or plain text
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'ingredients': self.ingredients,
            'created_at': self.created_at.isoformat()
        }

class ShoppingList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    items = db.Column(db.Text) # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'items': self.items,
            'created_at': self.created_at.isoformat(),
            'completed': self.completed
        }

# --- Helper Functions ---
def get_db_uri():
    return (
        f"postgresql://{os.getenv('DATABASE_USER')}:{os.getenv('DATABASE_PASSWORD')}"
        f"@{os.getenv('DATABASE_HOST')}:{os.getenv('DATABASE_PORT')}/{os.getenv('DATABASE_NAME')}"
    )

def refresh_db_connection():
    app.config['SQLALCHEMY_DATABASE_URI'] = get_db_uri()
    # In a real production app, handling dynamic DB switch is more complex.
    # For this local tool, we might rely on restart or separate implementation.
    # But let's try to update the engine if needed or just use current config.

# --- System & Config Routes ---

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'OK'}), 200

@app.route('/api/config', methods=['GET'])
def get_config():
    return jsonify({
        'database_host': os.getenv('DATABASE_HOST'),
        'database_port': os.getenv('DATABASE_PORT'),
        'database_name': os.getenv('DATABASE_NAME'),
        'database_user': os.getenv('DATABASE_USER'),
        'ollama_host': os.getenv('OLLAMA_HOST'),
        'ollama_model': os.getenv('OLLAMA_MODEL')
    })

@app.route('/api/config/update', methods=['POST'])
def update_config():
    data = request.json
    # Note: In a real app, writing to .env at runtime is tricky. 
    # Here we will try to update os.environ for the session and maybe write to .env
    try:
        if 'database_host' in data: os.environ['DATABASE_HOST'] = data['database_host']
        if 'database_port' in data: os.environ['DATABASE_PORT'] = data['database_port']
        if 'database_name' in data: os.environ['DATABASE_NAME'] = data['database_name']
        if 'database_user' in data: os.environ['DATABASE_USER'] = data['database_user']
        if 'database_password' in data and data['database_password']: 
            os.environ['DATABASE_PASSWORD'] = data['database_password']
        
        if 'ollama_host' in data: os.environ['OLLAMA_HOST'] = data['ollama_host']
        if 'ollama_model' in data: os.environ['OLLAMA_MODEL'] = data['ollama_model']

        # Update SQL Alchemy config
        app.config['SQLALCHEMY_DATABASE_URI'] = get_db_uri()
        
        return jsonify({'status': 'OK', 'message': 'Configuration updated (session only)'})
    except Exception as e:
        return jsonify({'status': 'ERROR', 'message': str(e)}), 500

@app.route('/api/test-db', methods=['POST'])
def test_db():
    try:
        # Try to connect
        with app.app_context():
            db.engine.connect()
        return jsonify({'status': 'OK', 'message': 'Połączenie z bazą danych udane!'})
    except Exception as e:
        return jsonify({'status': 'ERROR', 'message': f'Błąd połączenia: {str(e)}'}), 500

@app.route('/api/test-ollama', methods=['POST'])
def test_ollama():
    host = os.getenv('OLLAMA_HOST')
    model = os.getenv('OLLAMA_MODEL')
    try:
        # Simple generation to test
        prompt = "Say hello in Polish"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        # Increased timeout to 10 seconds for test
        response = requests.post(f"{host}/api/generate", json=payload, timeout=10)
        if response.status_code == 200:
            return jsonify({'status': 'OK', 'message': f'Ollama działa! Odpowiedź: {response.json().get("response", "")}'})
        else:
             return jsonify({'status': 'ERROR', 'message': f'Ollama błąd: {response.status_code}'}), 500
    except Exception as e:
        return jsonify({'status': 'ERROR', 'message': f'Ollama błąd: {str(e)}'}), 500

@app.route('/api/ollama-models', methods=['GET'])
def get_ollama_models():
    """Pobierz listę dostępnych modeli Ollama"""
    ollama_host = os.getenv('OLLAMA_HOST')
    try:
        # Increased timeout to 10 seconds
        response = requests.get(f"{ollama_host}/api/tags", timeout=10)
        
        if response.status_code == 200:
            models_data = response.json()
            # Ekstrakcja nazw modeli
            models = [
                {
                    'name': model['name'],
                    'size': model.get('size', 0),
                    'modified': model.get('modified_at', '')
                }
                for model in models_data.get('models', [])
            ]
            return jsonify({
                'status': 'OK',
                'models': models
            }), 200
        else:
            return jsonify({
                'status': 'ERROR',
                'message': f'Błąd Ollama: {response.status_code}'
            }), 500
            
    except requests.exceptions.Timeout:
        return jsonify({
            'status': 'ERROR',
            'message': 'Timeout: Ollama nie odpowiada'
        }), 500
    except Exception as e:
        return jsonify({
            'status': 'ERROR',
            'message': str(e)
        }), 500

# --- Product Routes ---
@app.route('/api/products', methods=['GET'])
def get_products():
    # Only return available products explicitly marked as 'TAK'
    products = Product.query.filter_by(available='TAK').all()
    return jsonify([p.to_dict() for p in products])

@app.route('/api/products', methods=['POST'])
def add_product():
    data = request.json
    try:
        new_product = Product(
            name=data['name'],
            category=data.get('category'),
            quantity=float(data['quantity']),
            # unit ignored as not in DB
            price=float(data.get('price', 0)),
            expiry_date=datetime.strptime(data['expiry_date'], '%Y-%m-%d').date() if data.get('expiry_date') else None,
            available='TAK', # Default to available
            shop='MealPlanner' # Default shop name
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify(new_product.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/products/<int:id>', methods=['PUT'])
def update_product(id):
    product = Product.query.get_or_404(id)
    data = request.json
    try:
        if 'expiry_date' in data:
            if data['expiry_date']:
                product.expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()
            else:
                product.expiry_date = None
        
        if 'is_frozen' in data:
            product.is_frozen = bool(data['is_frozen'])
            
        db.session.commit()
        return jsonify(product.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({'result': 'Product deleted'})

# --- AI Suggestion Routes ---

def call_ollama(prompt):
    host = os.getenv('OLLAMA_HOST')
    model = os.getenv('OLLAMA_MODEL')
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    try:
        # Increased timeout to 120 seconds
        response = requests.post(f"{host}/api/generate", json=payload, timeout=120)
        if response.status_code == 200:
            return response.json().get('response', '')
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error: {str(e)}"

@app.route('/api/suggest-meal', methods=['POST'])
def suggest_meal():
    products = Product.query.all()
    product_list = ", ".join([f"{p.name} ({p.quantity} {p.unit})" for p in products])
    
    prompt = f"""
    Mam dostępne produkty: [{product_list}]. 
    Zasugeruj mi jeden prosty, smaczny posiłek, który mogę dzisiaj przygotować.
    Podaj nazwę posiłku, składniki i instrukcje przygotowania w 3-4 krokach.
    Odpowiedz w języku polskim.
    """
    
    suggestion = call_ollama(prompt)
    return jsonify({'suggestion': suggestion})

@app.route('/api/suggest-weekly-menu', methods=['POST'])
def suggest_weekly_menu():
    products = Product.query.all()
    product_list = ", ".join([f"{p.name} ({p.quantity} {p.unit})" for p in products])
    
    prompt = f"""
    Mam dostępne produkty: [{product_list}]. 
    Zaproponuj mi jadłospis na 7 dni, wykorzystując dostępne produkty.
    Dla każdego dnia podaj: śniadanie, obiad i kolację.
    Odpowiedz w języku polskim.
    """
    
    suggestion = call_ollama(prompt)
    return jsonify({'suggestion': suggestion})

@app.route('/api/suggest-shopping-list', methods=['POST'])
def suggest_shopping_list():
    products = Product.query.all()
    product_list = ", ".join([f"{p.name} ({p.quantity} {p.unit})" for p in products])
    
    prompt = f"""
    Mam produkty: [{product_list}]. 
    Jakie dodatki i produkty powinieneś kupić dla bogatszej i bardziej zróżnicowanej diety?
    Podaj konkretną listę 15-20 produktów do kupienia z ilościami.
    Odpowiedz w języku polskim.
    """
    
    suggestion = call_ollama(prompt)
    return jsonify({'suggestion': suggestion})

# --- Init DB ---
with app.app_context():
    # Attempt to create tables if connection is successful
    try:
        # db.create_all() # Schema exists externally
        print("Database connection ready.")
    except Exception as e:
        print(f"Failed to initialize database: {e}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
