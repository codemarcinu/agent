
from app import app, db
from sqlalchemy import inspect

with app.app_context():
    inspector = inspect(db.engine)
    
    print("--- Table: paragony_pozycje ---")
    columns = inspector.get_columns('paragony_pozycje')
    for c in columns:
        print(f"{c['name']} ({c['type']})")
        
    print("\n--- Table: paragony ---")
    columns = inspector.get_columns('paragony')
    for c in columns:
        print(f"{c['name']} ({c['type']})")
