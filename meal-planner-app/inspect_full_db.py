from app import app, db
from sqlalchemy import text

def inspect_full_schema():
    with app.app_context():
        # Get all tables
        tables = db.session.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE'"
        )).fetchall()
        
        table_names = [t[0] for t in tables]
        table_names.sort()
        
        print(f"Found {len(table_names)} tables: {', '.join(table_names)}\n")
        
        for table in table_names:
            print(f"=== TABLE: {table} ===")
            
            # Columns
            print("--- Columns ---")
            cols = db.session.execute(text(
                f"""
                SELECT column_name, data_type, is_nullable, column_default 
                FROM information_schema.columns 
                WHERE table_name='{table}' 
                ORDER BY ordinal_position
                """
            )).fetchall()
            for c in cols:
                nullable = "NULL" if c[2] == 'YES' else "NOT NULL"
                default = f"DEFAULT {c[3]}" if c[3] else ""
                print(f"  - {c[0]} ({c[1]}, {nullable}) {default}")
            
            # Constraints (PK, FK, Unique)
            print("\n--- Constraints ---")
            constraints = db.session.execute(text(
                f"""
                SELECT tc.constraint_name, tc.constraint_type, kcu.column_name, 
                       ccu.table_name AS foreign_table_name,
                       ccu.column_name AS foreign_column_name 
                FROM information_schema.table_constraints tc 
                JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name 
                LEFT JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name = tc.constraint_name 
                WHERE tc.table_name='{table}'
                """
            )).fetchall()
            
            if not constraints:
                print("  (None)")
            else:
                for c in constraints:
                    # Note: ccu join might be ambiguous for multiple columns, simple approach here
                    detail = f"{c[2]}"
                    if c[1] == 'FOREIGN KEY':
                        detail += f" -> {c[3]}.{c[4]}"
                    print(f"  - {c[0]} ({c[1]}): {detail}")

            # Indexes
            print("\n--- Indexes ---")
            indexes = db.session.execute(text(
                f"SELECT indexname, indexdef FROM pg_indexes WHERE tablename = '{table}'"
            )).fetchall()
            for i in indexes:
                print(f"  - {i[0]}: {i[1]}")
            
            print("\n" + "="*30 + "\n")

if __name__ == "__main__":
    inspect_full_schema()
