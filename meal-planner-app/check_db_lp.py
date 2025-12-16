from app import app, db
from sqlalchemy import text

def check_db():
    with app.app_context():
        print("=== Bazy dostępne (skipped - using current DB) ===")
        
        print("\n=== Tabele w bazie 'postgres' (current DB) ===")
        tables = db.session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")).fetchall()
        for t in tables:
            print(t[0])
            
        print("\n=== Kolumny w tabeli paragony_pozycje ===")
        try:
            columns = db.session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='paragony_pozycje' ORDER BY ordinal_position;")).fetchall()
            for c in columns:
                print(c[0])
                
            print("\n=== Test: czy kolumna 'lp' istnieje? ===")
            exists = db.session.execute(text("SELECT EXISTS(SELECT 1 FROM information_schema.columns WHERE table_name='paragony_pozycje' AND column_name='lp');")).scalar()
            print(f"Exists: {exists}")
            
        except Exception as e:
            print(f"Error checking columns: {e}")

if __name__ == "__main__":
    check_db()
