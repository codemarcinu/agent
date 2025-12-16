from app import app, db
from sqlalchemy import text

def run_migration():
    with app.app_context():
        try:
            print("Starting database migration v2...")
            
            # 1. Create user_preferences table
            print("Creating table 'user_preferences'...")
            create_preferences_sql = text("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id SERIAL PRIMARY KEY,
                    user_id INT,
                    allergen VARCHAR(100),
                    diet_type VARCHAR(50),
                    disliked_products TEXT,
                    liked_products TEXT
                );
            """)
            db.session.execute(create_preferences_sql)

            # 2. Create purchase_history table
            print("Creating table 'purchase_history'...")
            create_history_sql = text("""
                CREATE TABLE IF NOT EXISTS purchase_history (
                    id SERIAL PRIMARY KEY,
                    product_id BIGINT,
                    purchase_date DATE,
                    quantity NUMERIC,
                    price NUMERIC,
                    shop VARCHAR(100),
                    category VARCHAR(100)
                );
            """)
            db.session.execute(create_history_sql)

            # 3. Create product_usage table
            print("Creating table 'product_usage'...")
            create_usage_sql = text("""
                CREATE TABLE IF NOT EXISTS product_usage (
                    id SERIAL PRIMARY KEY,
                    product_id BIGINT,
                    used_date DATE,
                    used_amount NUMERIC,
                    meal_id INT
                );
            """)
            db.session.execute(create_usage_sql)

            # 4. Alter paragony_pozycje table
            print("Checking/Altering 'paragony_pozycje' table...")
            
            # Check for unit column
            check_unit_sql = text("SELECT column_name FROM information_schema.columns WHERE table_name='paragony_pozycje' AND column_name='unit';")
            if not db.session.execute(check_unit_sql).fetchone():
                print("Adding column 'unit'...")
                db.session.execute(text("ALTER TABLE paragony_pozycje ADD COLUMN unit VARCHAR(20) DEFAULT 'szt';"))
            else:
                print("Column 'unit' already exists.")

            # Check for created_at column
            check_created_at_sql = text("SELECT column_name FROM information_schema.columns WHERE table_name='paragony_pozycje' AND column_name='created_at';")
            if not db.session.execute(check_created_at_sql).fetchone():
                print("Adding column 'created_at'...")
                db.session.execute(text("ALTER TABLE paragony_pozycje ADD COLUMN created_at TIMESTAMP DEFAULT NOW();"))
            else:
                print("Column 'created_at' already exists.")

            db.session.commit()
            print("Migration v2 completed successfully.")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            db.session.rollback()

if __name__ == "__main__":
    run_migration()
