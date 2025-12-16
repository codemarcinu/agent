from app import app, db
from sqlalchemy import text

def run_migration():
    with app.app_context():
        try:
            print("Starting database migration v3 (Receipts)...")
            
            # 1. Create paragony table
            print("Creating table 'paragony'...")
            create_paragony_sql = text("""
                CREATE TABLE IF NOT EXISTS paragony (
                    id SERIAL PRIMARY KEY,
                    sklep VARCHAR(100),
                    data_zakupu DATE,
                    suma_total NUMERIC(10,2),
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            db.session.execute(create_paragony_sql)

            # 2. Add paragon_id to paragony_pozycje
            print("Adding 'paragon_id' to 'paragony_pozycje'...")
            check_col_sql = text("SELECT column_name FROM information_schema.columns WHERE table_name='paragony_pozycje' AND column_name='paragon_id';")
            if not db.session.execute(check_col_sql).fetchone():
                db.session.execute(text("ALTER TABLE paragony_pozycje ADD COLUMN paragon_id INT;"))
            else:
                print("Column 'paragon_id' already exists in 'paragony_pozycje'.")

            # 3. Add paragon_id to purchase_history
            print("Adding 'paragon_id' to 'purchase_history'...")
            check_hist_sql = text("SELECT column_name FROM information_schema.columns WHERE table_name='purchase_history' AND column_name='paragon_id';")
            if not db.session.execute(check_hist_sql).fetchone():
                db.session.execute(text("ALTER TABLE purchase_history ADD COLUMN paragon_id INT;"))
            else:
                print("Column 'paragon_id' already exists in 'purchase_history'.")

            db.session.commit()
            print("Migration v3 completed successfully.")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            db.session.rollback()

if __name__ == "__main__":
    run_migration()
