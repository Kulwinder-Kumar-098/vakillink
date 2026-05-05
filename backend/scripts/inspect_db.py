import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    print("Error: SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not found in .env")
    exit(1)

supabase = create_client(url, key)

tables = ["profiles", "lawyers", "query_history"]

for table in tables:
    try:
        # Try to select 1 row to see if table exists and what columns it has
        res = supabase.table(table).select("*").limit(1).execute()
        print(f"Table '{table}': EXISTS")
        if res.data:
            print(f"  Columns: {list(res.data[0].keys())}")
        else:
            print("  Table is empty.")
    except Exception as e:
        print(f"Table '{table}': ERROR - {e}")
