import os
import json
import requests
from datetime import datetime
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
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
    category = db.Column('produkt_kategoria', db.String(100))
    quantity = db.Column('ilosc', db.Numeric)
    price = db.Column('cena_jedn', db.Numeric)
    expiry_date = db.Column('data_waznosci', db.Date)
    available = db.Column('dostepny', db.String(10)) # TAK/NIE
    is_frozen = db.Column('czy_mrozonka', db.Boolean, default=False)
    shop = db.Column('sklep', db.String(100))
    purchase_date = db.Column('data_zakupow', db.Date)
    unit = db.Column('jednostka', db.String(20), default='szt')
    created_at = db.Column('created_at', db.DateTime, default=datetime.utcnow)
    paragon_id = db.Column(db.Integer, nullable=True)
    lp = db.Column(db.Integer, nullable=True)
    
    # New columns
    kod_produktu = db.Column(db.String(100))
    vat_proc = db.Column(db.Integer)
    suma_brutto = db.Column(db.Numeric(10,2))

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
            'shop': self.shop,
            'paragon_id': self.paragon_id,
            'lp': self.lp,
            'kod_produktu': self.kod_produktu,
            'vat_proc': self.vat_proc,
            'suma_brutto': float(self.suma_brutto) if self.suma_brutto else 0.0
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

class UserPreference(db.Model):
    __tablename__ = 'user_preferences'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, default=1) # Single user mode for now
    allergen = db.Column(db.String(100))
    diet_type = db.Column(db.String(50))
    disliked_products = db.Column(db.Text)
    liked_products = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'allergen': self.allergen,
            'diet_type': self.diet_type,
            'disliked_products': self.disliked_products,
            'liked_products': self.liked_products
        }

class PurchaseHistory(db.Model):
    __tablename__ = 'purchase_history'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.BigInteger)
    purchase_date = db.Column(db.Date)
    quantity = db.Column(db.Numeric)
    price = db.Column(db.Numeric)
    shop = db.Column(db.String(100))
    category = db.Column(db.String(100))
    paragon_id = db.Column(db.Integer, nullable=True)
    product_name = db.Column(db.String(200))

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'purchase_date': self.purchase_date.isoformat() if self.purchase_date else None,
            'quantity': float(self.quantity) if self.quantity else 0,
            'price': float(self.price) if self.price else 0,
            'shop': self.shop,
            'category': self.category,
            'product_name': self.product_name
        }

class ProductUsage(db.Model):
    __tablename__ = 'product_usage'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.BigInteger)
    used_date = db.Column(db.Date)
    used_amount = db.Column(db.Numeric)
    meal_id = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'used_date': self.used_date.isoformat(),
            'used_amount': float(self.used_amount) if self.used_amount else 0
        }

class Receipt(db.Model):
    __tablename__ = 'paragony'
    id = db.Column(db.Integer, primary_key=True)
    sklep = db.Column(db.String(100))
    data_zakupu = db.Column(db.Date)
    suma_total = db.Column(db.Numeric(10, 2))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'sklep': self.sklep,
            'data_zakupu': self.data_zakupu.isoformat() if self.data_zakupu else None,
            'suma_total': float(self.suma_total) if self.suma_total else 0.0,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
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

def call_ollama_safe(prompt, expect_json=False):
    host = os.getenv('OLLAMA_HOST')
    model = os.getenv('OLLAMA_MODEL')
    
    system_prompt = "Jesteś pomocnym asystentem kulinarnym. Odpowiadaj krótko i konkretnie."
    if expect_json:
        system_prompt += " Odpowiedz TYLKO poprawnym formatem JSON. Nie dodawaj markdown."

    payload = {
        "model": model,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "options": {
            "temperature": 0.3 if expect_json else 0.7
        }
    }
    
    try:
        # Increased timeout to 60 seconds
        response = requests.post(f"{host}/api/generate", json=payload, timeout=60)
        if response.status_code == 200:
            text = response.json().get('response', '')
            if expect_json:
                try:
                    # Clean markdown code blocks if present
                    clean_text = text.replace('```json', '').replace('```', '').strip()
                    return json.loads(clean_text)
                except json.JSONDecodeError:
                    # Try to find JSON in text if it has markdown hints
                    start = text.find('{')
                    end = text.rfind('}') + 1
                    if start != -1 and end != -1:
                        json_str = text[start:end]
                        try:
                            return json.loads(json_str)
                        except:
                            pass
                    print(f"Failed to parse JSON: {text}")
                    return None
            return text
        else:
            print(f"Ollama error: {response.text}")
            return None
    except Exception as e:
        print(f"Ollama exception: {str(e)}")
        return None

@app.route('/api/suggest-meal', methods=['POST'])
def suggest_meal():
    products = Product.query.filter_by(available='TAK').all()
    # Get user preferences
    prefs = UserPreference.query.filter_by(user_id=1).first()
    
    product_list = ", ".join([f"{p.name} ({p.quantity} {p.unit})" for p in products])
    
    pref_text = ""
    if prefs:
        if prefs.diet_type: pref_text += f"\nDieta: {prefs.diet_type}."
        if prefs.allergen: pref_text += f"\nUnikaj alergenów: {prefs.allergen}."
        if prefs.disliked_products: pref_text += f"\nNie lubię: {prefs.disliked_products}."

    prompt = f"""
    Mam dostępne produkty: [{product_list}].
    {pref_text} 
    Zasugeruj mi jeden prosty, smaczny posiłek, który mogę dzisiaj przygotować.
    Podaj nazwę posiłku, składniki (z ilościami) i instrukcje przygotowania w krokach.
    Format JSON:
    {{
        "meal_name": "Nazwa",
        "ingredients": ["item 1", "item 2"],
        "steps": ["step 1", "step 2"]
    }}
    """
    
    suggestion = call_ollama_safe(prompt, expect_json=True)
    
    # Fallback to plain text if JSON fails or manual construction
    if not suggestion:
        # Retry with simpler prompt or just return error/text
        return jsonify({'suggestion': "Nie udało się wygenerować sugestii. Spróbuj ponownie."})
        
    # Format for frontend (which expects HTML/Markdown currently, but we can send structured)
    # The frontend expects 'suggestion' string with HTML/Markdown.
    # Let's convert JSON back to nice HTML for now to keep frontend compatible, 
    # or update frontend to handle JSON. Implementation Plan said "Update backend...". 
    # Let's return JSON and update Frontend to handle it.
    
    return jsonify({'suggestion': suggestion, 'is_json': True})

@app.route('/api/suggest-weekly-menu', methods=['POST'])
def suggest_weekly_menu():
    products = Product.query.filter_by(available='TAK').all()
    product_list = ", ".join([f"{p.name} ({p.quantity} {p.unit})" for p in products])
    
    prompt = f"""
    Mam dostępne produkty: [{product_list}]. 
    Zaproponuj mi jadłospis na 7 dni.
    Dla każdego dnia (Dzień 1...7) podaj: śniadanie, obiad i kolację.
    Odpowiedz w formacie Markdown.
    """
    
    suggestion = call_ollama_safe(prompt, expect_json=False)
    return jsonify({'suggestion': suggestion, 'is_json': False})

@app.route('/api/suggest-shopping-list', methods=['POST'])
def suggest_shopping_list():
    products = Product.query.filter_by(available='TAK').all()
    product_list = ", ".join([f"{p.name} ({p.quantity} {p.unit})" for p in products])
    
    prompt = f"""
    Mam produkty: [{product_list}]. 
    Jakie dodatki i produkty powinieneś kupić dla bogatszej diety?
    Wymień 15-20 produktów.
    Format JSON: ["produkt 1", "produkt 2", ...]
    """
    
    suggestion = call_ollama_safe(prompt, expect_json=True)
    if not suggestion:
        suggestion = "Błąd generowania."
    
    return jsonify({'suggestion': suggestion, 'is_json': True})

# --- Statistics & Data Routes ---

@app.route('/api/products/all', methods=['GET'])
def get_all_products():
    """Return all products including history (unavailable ones)"""
    products = Product.query.order_by(Product.purchase_date.desc()).all()
    return jsonify([p.to_dict() for p in products])

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    try:
        # Total spend query (sum of price * quantity for all entries)
        # Note: price is per unit usually.
        # Use SQL for efficiency
        
        # 1. Total Spend (All time)
        total_spend = db.session.query(func.sum(Product.price * Product.quantity)).scalar() or 0
        
        # 2. Total Products Count
        total_count = Product.query.count()
        
        # 3. Available vs Used
        available_count = Product.query.filter_by(available='TAK').count()
        
        # 4. Top Categories
        top_cats = db.session.query(
            Product.category, func.count(Product.id)
        ).group_by(Product.category).order_by(func.count(Product.id).desc()).limit(5).all()
        
        categories_data = [{'name': c[0], 'count': c[1]} for c in top_cats]
        
        # 5. Monthly Spend (Last 6 months) - Requires parsing purchase_date
        # Simple implementation: group by year-month
        # PostgreSQL specific: to_char
        monthly_spend = db.session.query(
            func.to_char(Product.purchase_date, 'YYYY-MM'),
            func.sum(Product.price * Product.quantity)
        ).group_by(func.to_char(Product.purchase_date, 'YYYY-MM'))\
         .order_by(func.to_char(Product.purchase_date, 'YYYY-MM').desc())\
         .limit(6).all()
         
        monthly_data = [{'month': m[0], 'total': float(m[1]) if m[1] else 0} for m in monthly_spend]

        # 6. Avg Basket Value
        avg_basket = db.session.query(func.avg(Receipt.suma_total)).scalar() or 0

        return jsonify({
            'total_spend': float(total_spend),
            'total_items': total_count,
            'available_items': available_count,
            'top_categories': categories_data,
            'monthly_spend': monthly_data,
            'avg_basket': float(avg_basket)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/receipts', methods=['GET', 'POST'])
def handle_receipts():
    if request.method == 'GET':
        receipts = Receipt.query.order_by(Receipt.data_zakupu.desc()).limit(20).all()
        return jsonify([r.to_dict() for r in receipts])
        
    if request.method == 'POST':
        data = request.json
        try:
            # Create Receipt
            receipt = Receipt(
                sklep=data.get('shop', 'Nieznany'),
                data_zakupu=datetime.strptime(data.get('date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d').date(),
                suma_total=0 # Will calc
            )
            db.session.add(receipt)
            db.session.flush() # Get ID
            
            total = 0
            
            # Create products linked to receipt
            for item in data.get('items', []):
                price = float(item.get('price', 0))
                qty = float(item.get('quantity', 1))
                total += price * qty
                
                new_product = Product(
                    name=item['name'],
                    category=item.get('category'),
                    quantity=qty,
                    price=price,
                    unit=item.get('unit', 'szt'),
                    expiry_date=datetime.strptime(item['expiry_date'], '%Y-%m-%d').date() if item.get('expiry_date') else None,
                    available='TAK',
                    shop=receipt.sklep,
                    purchase_date=receipt.data_zakupu,
                    paragon_id=receipt.id
                )
                db.session.add(new_product)
                
                # Also add to history immediately
                history = PurchaseHistory(
                    product_id=None, # It's new, we don't have ID yet, but after commit we can. Or just loose coupling.
                    # Using loose coupling for history table as it is a log
                    purchase_date=receipt.data_zakupu,
                    quantity=qty,
                    price=price,
                    shop=receipt.sklep,
                    category=item.get('category'),
                    paragon_id=receipt.id,
                    product_name=item['name']
                )
                db.session.add(history)

            receipt.suma_total = total
            db.session.commit()
            
            return jsonify({'status': 'OK', 'receipt': receipt.to_dict()}), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

@app.route('/api/receipts/<int:id>', methods=['GET'])
def get_receipt(id):
    receipt = Receipt.query.get_or_404(id)
    # Get products for this receipt from history (as they might be deleted from active products)
    products = PurchaseHistory.query.filter_by(paragon_id=id).all()
    
    return jsonify({
        'receipt': receipt.to_dict(),
        'items': [p.to_dict() for p in products]
    })

@app.route('/api/preferences', methods=['GET', 'POST'])
def handle_preferences():
    if request.method == 'POST':
        data = request.json
        pref = UserPreference.query.filter_by(user_id=1).first()
        if not pref:
            pref = UserPreference(user_id=1)
            db.session.add(pref)
        
        pref.allergen = data.get('allergen')
        pref.diet_type = data.get('diet_type')
        pref.disliked_products = data.get('disliked_products')
        pref.liked_products = data.get('liked_products')
        
        db.session.commit()
        return jsonify(pref.to_dict())
    else:
        pref = UserPreference.query.filter_by(user_id=1).first()
        if pref:
            return jsonify(pref.to_dict())
        return jsonify({})

@app.route('/api/products/<int:id>/usage', methods=['POST'])
def track_usage(id):
    product = Product.query.get_or_404(id)
    data = request.json
    amount = float(data.get('amount', 0))
    
    if amount > 0:
        # Create usage record
        usage = ProductUsage(
            product_id=product.id,
            used_date=datetime.now().date(),
            used_amount=amount
        )
        db.session.add(usage)
        
        # Update product
        current_qty = float(product.quantity)
        new_qty = max(0, current_qty - amount)
        product.quantity = new_qty
        
        if new_qty == 0:
            product.available = 'NIE'
            
        db.session.commit()
        return jsonify({'status': 'OK', 'new_quantity': new_qty})
    
    return jsonify({'error': 'Invalid amount'}), 400

if __name__ == '__main__':

    app.run(debug=True, host='0.0.0.0', port=5000)
