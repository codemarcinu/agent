from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        # Check columns
        result = db.session.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'paragony_pozycje';"))
        print("\n--- SCHEMA OF paragony_pozycje ---")
        for row in result:
            print(f"{row[0]}: {row[1]}")
            
        # Check sample data
        result = db.session.execute(text("SELECT * FROM paragony_pozycje LIMIT 3;"))
        print("\n--- SAMPLE DATA ---")
        for row in result:
            print(row)
            
    except Exception as e:
        print(f"Error: {e}")
