from app import app, db
from sqlalchemy import text

def run_migration():
    with app.app_context():
        try:
            print("Starting database migration v4 (History Name)...")
            
            # Add name to purchase_history
            print("Adding 'product_name' to 'purchase_history'...")
            check_col_sql = text("SELECT column_name FROM information_schema.columns WHERE table_name='purchase_history' AND column_name='product_name';")
            if not db.session.execute(check_col_sql).fetchone():
                db.session.execute(text("ALTER TABLE purchase_history ADD COLUMN product_name VARCHAR(200);"))
                print("Column 'product_name' added.")
            else:
                print("Column 'product_name' already exists.")

            db.session.commit()
            print("Migration v4 completed successfully.")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            db.session.rollback()

if __name__ == "__main__":
    run_migration()
