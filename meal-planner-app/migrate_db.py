from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        # Check if column exists
        check_sql = text("SELECT column_name FROM information_schema.columns WHERE table_name='paragony_pozycje' AND column_name='czy_mrozonka';")
        result = db.session.execute(check_sql).fetchone()
        
        if not result:
            print("Adding column 'czy_mrozonka'...")
            alter_sql = text("ALTER TABLE paragony_pozycje ADD COLUMN czy_mrozonka BOOLEAN DEFAULT FALSE;")
            db.session.execute(alter_sql)
            db.session.commit()
            print("Column added successfully.")
        else:
            print("Column 'czy_mrozonka' already exists.")
            
    except Exception as e:
        print(f"Error: {e}")
        db.session.rollback()
