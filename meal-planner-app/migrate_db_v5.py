from app import app, db
from sqlalchemy import text

def run_migration():
    with app.app_context():
        try:
            print("Starting database migration v5 (Receipt Updated At)...")
            
            # Add updated_at to paragony
            print("Adding 'updated_at' to 'paragony'...")
            check_col_sql = text("SELECT column_name FROM information_schema.columns WHERE table_name='paragony' AND column_name='updated_at';")
            if not db.session.execute(check_col_sql).fetchone():
                db.session.execute(text("ALTER TABLE paragony ADD COLUMN updated_at TIMESTAMP DEFAULT NOW();"))
                print("Column 'updated_at' added.")
            else:
                print("Column 'updated_at' already exists.")

            db.session.commit()
            print("Migration v5 completed successfully.")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            db.session.rollback()

if __name__ == "__main__":
    run_migration()
