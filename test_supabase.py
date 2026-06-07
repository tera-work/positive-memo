# python test_supabase.pyで実行

from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

print("URL =", os.getenv("SUPABASE_URL"))
print("KEY =", os.getenv("SUPABASE_KEY"))

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)