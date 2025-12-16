from app import app, db
from sqlalchemy import text

def clear_data():
    with app.app_context():
        try:
            print("Cleaning all database tables...")
            
            # Order to avoid potential FK issues (though currently loose)
            tables = [
                'product',          # Legacy/Other
                'product_usage',
                'purchase_history',
                'paragony_pozycje', # Products
                'paragony',         # Receipts
                'shopping_list',
                'meal',
                'user_preferences'
            ]
            
            for table in tables:
                print(f"Truncating {table}...")
                # Use TRUNCATE for speed and cleanliness, CASCADE to handle FKs if any
                try:
                    db.session.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;"))
                except Exception as e:
                    print(f"Could not truncate {table} (might not exist or other error): {e}")
                    # Fallback to DELETE
                    db.session.execute(text(f"DELETE FROM {table};"))
            
            db.session.commit()
            print("All tables cleared successfully!")
            
        except Exception as e:
            print(f"Error clearing data: {e}")
            db.session.rollback()

if __name__ == "__main__":
    confirm = input("Are you sure you want to delete ALL data? (yes/no): ")
    if confirm.lower() == 'yes':
        clear_data()
    else:
        print("Operation cancelled.")
