from app import app, db
from sqlalchemy import text

def verify_optimization():
    with app.app_context():
        print("=== Verifying Optimizations ===")
        
        # Check Index
        print("\nChecking Index 'idx_paragony_pozycje_dostepny':")
        index_exists = db.session.execute(text(
            "SELECT 1 FROM pg_indexes WHERE indexname = 'idx_paragony_pozycje_dostepny'"
        )).scalar()
        if index_exists:
            print("[OK] Index found.")
        else:
            print("[FAIL] Index NOT found.")
            
        # Check Foreign Key
        print("\nChecking Foreign Key 'fk_paragon_id':")
        fk_exists = db.session.execute(text(
            "SELECT 1 FROM information_schema.table_constraints "
            "WHERE constraint_name = 'fk_paragon_id' AND table_name = 'paragony_pozycje'"
        )).scalar()
        
        if fk_exists:
            print("[OK] Foreign Key constraint found.")
            
            # Verify CASCADE DELETE behavior?
            # Ideally yes, but that requires inserting dummy data and deleting it.
            # For now, checking the existence of the constraint is good enough for structure verification.
            print("     (Constraint exists in information_schema)")
        else:
             print("[FAIL] Foreign Key constraint NOT found.")

if __name__ == "__main__":
    verify_optimization()
