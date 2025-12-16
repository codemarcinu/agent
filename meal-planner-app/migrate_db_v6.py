from app import app, db
from sqlalchemy import text

def run_migration():
    with app.app_context():
        try:
            print("Starting database migration v6 (Add 'lp' column)...")
            
            # Add lp to paragony_pozycje
            print("Adding 'lp' to 'paragony_pozycje'...")
            check_col_sql = text("SELECT column_name FROM information_schema.columns WHERE table_name='paragony_pozycje' AND column_name='lp';")
            if not db.session.execute(check_col_sql).fetchone():
                # nullable=True for existing records
                db.session.execute(text("ALTER TABLE paragony_pozycje ADD COLUMN lp INTEGER;"))
                print("Column 'lp' added.")
            else:
                print("Column 'lp' already exists.")

            db.session.commit()
            print("Migration v6 completed successfully.")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            db.session.rollback()

if __name__ == "__main__":
    run_migration()
