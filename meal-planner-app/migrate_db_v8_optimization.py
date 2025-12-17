from app import app, db
from sqlalchemy import text

def migrate():
    with app.app_context():
        try:
            print("--- Adding Index on 'dostepny' ---")
            db.session.execute(text(
                "CREATE INDEX IF NOT EXISTS idx_paragony_pozycje_dostepny ON paragony_pozycje(dostepny)"
            ))
            print("Index created successfully.")

            print("\n--- Identify Orphaned Records ---")
            # Before adding FK, we must check for orphans
            orphans = db.session.execute(text(
                "SELECT COUNT(*) FROM paragony_pozycje pp "
                "LEFT JOIN paragony p ON pp.paragon_id = p.id "
                "WHERE p.id IS NULL AND pp.paragon_id IS NOT NULL"
            )).scalar()
            
            if orphans > 0:
                print(f"WARNING: Found {orphans} orphaned records in paragony_pozycje. Fixing them by setting paragon_id to NULL...")
                # Option 1: Set to NULL (safest if we want to keep data)
                db.session.execute(text(
                    "UPDATE paragony_pozycje pp "
                    "SET paragon_id = NULL "
                    "WHERE NOT EXISTS (SELECT 1 FROM paragony p WHERE p.id = pp.paragon_id)"
                ))
                print("Orphans corrected.")
            else:
                print("No orphaned records found.")

            print("\n--- Adding Foreign Key Constraint ---")
            # We need to drop it first if it exists (though inspecting earlier showed none)
            # Safe approach: try adding it
            db.session.execute(text(
                "ALTER TABLE paragony_pozycje "
                "ADD CONSTRAINT fk_paragon_id "
                "FOREIGN KEY (paragon_id) "
                "REFERENCES paragony(id) "
                "ON DELETE CASCADE"
            ))
            print("Foreign Key constraint added successfully.")
            
            db.session.commit()
            print("\nMigration completed successfully.")
            
        except Exception as e:
            db.session.rollback()
            print(f"\nMigration FAILED: {e}")

if __name__ == "__main__":
    migrate()
