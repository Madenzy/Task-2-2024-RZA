import pandas as pd
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
import os

# ---------- CONFIGURATION ----------
CSV_FILE = "MOCK_DATA.csv"
DB_FILE = "rza_task_2.db"
TABLE_NAME = "cards"




def import_csv_to_sqlite(csv_path, db_path, table_name):
    # Validate CSV file existence
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file '{csv_path}' not found.")

    # Create SQLAlchemy engine for SQLite using the project DB file in instance/
    basedir = os.path.abspath(os.path.dirname(__file__))
    engine = create_engine(f"sqlite:///{os.path.join(basedir, 'instance', db_path)}")

    # Read CSV into DataFrame
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        raise ValueError(f"Error reading CSV: {e}")

    if df.empty:
        raise ValueError("CSV file is empty. Nothing to import.")

    # Optional: Create table schema dynamically if not exists
    metadata = MetaData()
    if not engine.dialect.has_table(engine.connect(), table_name):
        # Example: create columns based on CSV headers (all as String)
        columns = [Column(col, String) for col in df.columns]
        table = Table(table_name, metadata, Column("id", Integer, primary_key=True, autoincrement=True), *columns)
        metadata.create_all(engine)
    print(df)
    # Insert data into SQLite
    try:
        df.to_sql(table_name, con=engine, if_exists='append', index=False)
        print(f"✅ Successfully imported {len(df)} rows into '{table_name}' in '{db_path}'.")
    except Exception as e:
        raise RuntimeError(f"Error inserting data into SQLite: {e}")

if __name__ == "__main__":
    try:
        import_csv_to_sqlite(CSV_FILE, DB_FILE, TABLE_NAME)
    except Exception as err:
        print(f"❌ {err}")
