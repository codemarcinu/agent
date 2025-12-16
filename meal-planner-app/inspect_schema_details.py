from app import app, db
from sqlalchemy import text

def inspect_schema():
    with app.app_context():
        print("=== Columns in 'paragony' ===")
        cols = db.session.execute(text(
            "SELECT column_name, data_type FROM information_schema.columns WHERE table_name='paragony'"
        )).fetchall()
        for c in cols:
            print(f"{c[0]} ({c[1]})")

        print("\n=== Constraints/Indexes on 'paragony' ===")
        # Check for unique constraints or indexes that might support the ON CONFLICT
        indexes = db.session.execute(text(
            "SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'paragony'"
        )).fetchall()
        for i in indexes:
            print(f"{i[0]}: {i[1]}")

        print("\n=== Columns in 'paragony_pozycje' ===")
        cols = db.session.execute(text(
            "SELECT column_name, data_type FROM information_schema.columns WHERE table_name='paragony_pozycje'"
        )).fetchall()
        for c in cols:
            print(f"{c[0]} ({c[1]})")

if __name__ == "__main__":
    inspect_schema()
