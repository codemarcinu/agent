
from app import app, db, Product, Receipt
from datetime import datetime

def fix_orphans():
    with app.app_context():
        # Find orphans
        orphans = Product.query.filter(Product.paragon_id == None).all()
        
        if not orphans:
            print("No orphaned items found. All good!")
            return

        print(f"Found {len(orphans)} orphaned items.")
        
        # Create a new receipt for them
        # We'll use the current date or the date of the first item
        first_date = orphans[0].created_at.date() if orphans[0].created_at else datetime.now().date()
        
        receipt = Receipt(
            sklep="Produkty Importowane (Naprawa)",
            data_zakupu=first_date,
            suma_total=0 # Will calc
        )
        db.session.add(receipt)
        db.session.flush() # ID
        
        total = 0
        for p in orphans:
            p.paragon_id = receipt.id
            # Estimate price if 0? No, just sum what we have
            price = float(p.price) if p.price else 0
            qty = float(p.quantity) if p.quantity else 0
            total += price * qty
            
        receipt.suma_total = total
        db.session.commit()
        
        print(f"Successfully linked {len(orphans)} items to new Receipt ID {receipt.id}.")
        print(f"Receipt Total: {total:.2f}")

if __name__ == "__main__":
    fix_orphans()
