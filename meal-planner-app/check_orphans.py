
from app import app, db, Product
from sqlalchemy import text

with app.app_context():
    # Count total and nulls
    total = db.session.query(Product).count()
    nulls = db.session.query(Product).filter(Product.paragon_id == None).count()
    
    print(f"Total items: {total}")
    print(f"Items without paragon_id: {nulls}")
    
    if nulls > 0:
        print("\n--- Sample Missing IDs ---")
        items = db.session.query(Product).filter(Product.paragon_id == None).limit(10).all()
        for i in items:
            print(f"ID: {i.id}, Name: {i.name}, Created: {i.created_at}, Qty: {i.quantity}")

    # Also check raw SQL just in case
    # print("\n--- Raw SQL Check ---")
    # with db.engine.connect() as conn:
    #     result = conn.execute(text("SELECT * FROM paragony_pozycje WHERE paragon_id IS NULL LIMIT 5"))
    #     for row in result:
    #         print(row)
