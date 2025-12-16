from app import app, db
from sqlalchemy import text

def run_migration():
    with app.app_context():
        try:
            print("Starting database migration v7 (Align with User SQL)...")
            
            # --- Table: paragony_pozycje ---
            print("Migrating 'paragony_pozycje'...")
            
            # 1. Rename kategoria -> produkt_kategoria
            # Check if 'kategoria' exists and 'produkt_kategoria' does not
            cols = db.session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='paragony_pozycje';")).fetchall()
            col_names = [c[0] for c in cols]
            
            if 'kategoria' in col_names and 'produkt_kategoria' not in col_names:
                print("Renaming 'kategoria' to 'produkt_kategoria'...")
                db.session.execute(text("ALTER TABLE paragony_pozycje RENAME COLUMN kategoria TO produkt_kategoria;"))
            
            # 2. Rename unit -> jednostka
            if 'unit' in col_names and 'jednostka' not in col_names:
                print("Renaming 'unit' to 'jednostka'...")
                db.session.execute(text("ALTER TABLE paragony_pozycje RENAME COLUMN unit TO jednostka;"))

            # 3. Add missing columns
            # kod_produktu, vat_proc, suma_brutto
            
            # Refresh col names after rename
            cols = db.session.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='paragony_pozycje';")).fetchall()
            col_names = [c[0] for c in cols]

            if 'kod_produktu' not in col_names:
                print("Adding 'kod_produktu'...")
                db.session.execute(text("ALTER TABLE paragony_pozycje ADD COLUMN kod_produktu VARCHAR(100);"))
            
            if 'vat_proc' not in col_names:
                print("Adding 'vat_proc'...")
                db.session.execute(text("ALTER TABLE paragony_pozycje ADD COLUMN vat_proc INTEGER;")) # Assuming int %, e.g. 23
                
            if 'suma_brutto' not in col_names:
                print("Adding 'suma_brutto'...")
                db.session.execute(text("ALTER TABLE paragony_pozycje ADD COLUMN suma_brutto NUMERIC(10,2);"))

            # --- Table: paragony ---
            print("Migrating 'paragony'...")
            
            # 4. Fix Unique Constraint for ON CONFLICT
            # Drop old index if exists
            # We need to find the name of the unique index on (sklep, data_zakupu, numer_paragonu) or similar
            indexes = db.session.execute(text("SELECT indexname FROM pg_indexes WHERE tablename = 'paragony';")).fetchall()
            idx_names = [i[0] for i in indexes]
            
            if 'idx_unique_receipt' in idx_names:
                print("Dropping old index 'idx_unique_receipt'...")
                db.session.execute(text("DROP INDEX idx_unique_receipt;"))
                
            if 'paragony_sklep_data_zakupu_numer_paragonu_key' not in idx_names:
                 print("Adding constraint unique (sklep, data_zakupu, numer_paragonu)...")
                 # We use a named constraint/index to be clean
                 # Note: Postgres allows multiple unique indexes.
                 # The user SQL uses: ON CONFLICT (sklep, data_zakupu, numer_paragonu)
                 # This requires a unique index on these 3 columns.
                 db.session.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS paragony_upsert_idx ON paragony (sklep, data_zakupu, numer_paragonu);"))

            db.session.commit()
            print("Migration v7 completed successfully.")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            db.session.rollback()

if __name__ == "__main__":
    run_migration()
