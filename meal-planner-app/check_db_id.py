
from app import app, db
from sqlalchemy import text

with app.app_context():
    # 1. Check existing rows
    print("--- Rows in paragony_pozycje ---")
    rows = db.session.execute(text("SELECT id, produkt FROM paragony_pozycje LIMIT 5;")).fetchall()
    for r in rows:
        print(r)
        
    # 2. Check id column definition (raw SQL approximation)
    print("\n--- Column Info ---")
    # Postgres specific query to retrieve column default/identity
    try:
        col_info = db.session.execute(text("""
            SELECT column_name, column_default, is_identity 
            FROM information_schema.columns 
            WHERE table_name = 'paragony_pozycje' AND column_name = 'id';
        """)).fetchone()
        print(col_info)
    except Exception as e:
        print(e)
